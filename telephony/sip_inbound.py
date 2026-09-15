import os
import json
import base64
import html
import asyncio
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from database.db import init_db, get_db_connection
from clinical.prompt import GREETING_MESSAGE
from voice.engine import ReceptionistVoiceEngine

app = FastAPI(title="Pinnacle AI Voice Receptionist & SIP Gateway")

engine = ReceptionistVoiceEngine()

@app.on_event("startup")
async def on_startup():
    await init_db()

@app.get("/")
async def index():
    return {
        "service": "Pinnacle AI Voice Receptionist",
        "client": "High Springs Pediatrics and Primary Care",
        "physician": "Dr. Nasir Ahmed, M.D.",
        "phone_number": "+1 (386) 639-0334",
        "carrier": "Telnyx Dedicated SIP / TeXML",
        "status": "online"
    }

# --- Telnyx Inbound Webhook ---
@app.api_route("/api/telephony/telnyx/inbound", methods=["GET", "POST"])
async def telnyx_inbound(req: Request):
    """
    Initial greeting when caller dials +1 (386) 639-0334.
    """
    greeting = html.escape(GREETING_MESSAGE)
    texml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="AWS.Polly.Joanna">{greeting}</Say>
    <Gather input="speech" timeout="10" speechTimeout="auto" action="/api/telephony/telnyx/gather" method="POST" />
    <Redirect method="POST">/api/telephony/telnyx/retry</Redirect>
</Response>"""
    return Response(content=texml, media_type="text/xml")

# --- Telnyx Retry on Silence Webhook ---
@app.api_route("/api/telephony/telnyx/retry", methods=["GET", "POST"])
async def telnyx_retry(req: Request):
    """
    Keeps call alive if user pauses or carrier disclaimer caused a delay.
    """
    texml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="AWS.Polly.Joanna">I'm still here. How can I help you with High Springs Pediatrics today?</Say>
    <Gather input="speech" timeout="10" speechTimeout="auto" action="/api/telephony/telnyx/gather" method="POST" />
    <Say voice="AWS.Polly.Joanna">Thank you for calling High Springs Pediatrics and Primary Care. Goodbye!</Say>
</Response>"""
    return Response(content=texml, media_type="text/xml")

# --- Telnyx Gather Speech Webhook ---
@app.api_route("/api/telephony/telnyx/gather", methods=["GET", "POST"])
async def telnyx_gather(req: Request):
    """
    Processes caller speech, invokes clinical reasoning/tools, and speaks answer.
    """
    form_data = {}
    try:
        form = await req.form()
        form_data = dict(form)
    except Exception:
        pass

    speech_result = form_data.get("SpeechResult", "").strip()
    print(f"\n==========================================")
    print(f"[Telnyx Inbound Call] Patient said: '{speech_result}'")
    print(f"==========================================")

    if not speech_result:
        # User was silent, route to retry instead of hanging up
        texml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="AWS.Polly.Joanna">I'm listening. Could you please repeat how I can help you today?</Say>
    <Gather input="speech" timeout="10" speechTimeout="auto" action="/api/telephony/telnyx/gather" method="POST" />
    <Redirect method="POST">/api/telephony/telnyx/retry</Redirect>
</Response>"""
        return Response(content=texml, media_type="text/xml")

    # Generate Sarah's clinical response
    try:
        agent_resp = await engine.generate_response(speech_result)
        raw_reply = agent_resp.get("text", "Thank you for that information. How else can I assist you?")
        reply_text = html.escape(raw_reply)
        print(f"[Sarah Reply]: {raw_reply}")
    except Exception as err:
        print(f"[Engine Error]: {err}")
        reply_text = "Thank you for providing those details. Our clinical team at High Springs Pediatrics has noted your request. Is there anything else I can assist with?"

    texml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="AWS.Polly.Joanna">{reply_text}</Say>
    <Gather input="speech" timeout="10" speechTimeout="auto" action="/api/telephony/telnyx/gather" method="POST" />
    <Redirect method="POST">/api/telephony/telnyx/retry</Redirect>
</Response>"""
    return Response(content=texml, media_type="text/xml")

# --- Browser Audio Call Simulator ---
@app.get("/call", response_class=HTMLResponse)
async def call_interface():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Pinnacle AI - Live Voice Receptionist Tester</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
            .card { background: #1e293b; border-radius: 16px; padding: 32px; width: 480px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 1px solid #334155; }
            h2 { margin-top: 0; color: #38bdf8; font-size: 24px; text-align: center; }
            .status { text-align: center; padding: 12px; border-radius: 8px; background: #0f172a; margin: 16px 0; font-size: 14px; color: #94a3b8; }
            .log { height: 260px; overflow-y: auto; background: #0f172a; border-radius: 8px; padding: 12px; font-size: 13px; line-height: 1.5; border: 1px solid #334155; margin-bottom: 16px; }
            .input-group { display: flex; gap: 8px; }
            input { flex: 1; padding: 12px; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: #fff; font-size: 14px; }
            button { background: #0284c7; color: white; border: none; padding: 12px 20px; border-radius: 8px; font-weight: 600; cursor: pointer; }
            button:hover { background: #0369a1; }
            .badge { display: inline-block; font-size: 11px; background: #0369a1; color: #e0f2fe; padding: 2px 8px; border-radius: 4px; margin-bottom: 8px; }
        </style>
    </head>
    <body>
        <div class="card">
            <span class="badge">SIP / Tel-Agent Simulation</span>
            <h2>🩺 High Springs Pediatrics</h2>
            <div class="status" id="statusBox">Sarah (AI Receptionist) is ready. Phone: +1 (386) 639-0334</div>
            <div class="log" id="chatLog">
                <div style="color: #38bdf8;"><strong>Sarah:</strong> """ + GREETING_MESSAGE + """</div>
            </div>
            <div class="input-group">
                <input type="text" id="userInput" placeholder="Say something (e.g. 'I want to book an appointment for Leo')..." autofocus />
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
        <script>
            const chatLog = document.getElementById('chatLog');
            const userInput = document.getElementById('userInput');
            const statusBox = document.getElementById('statusBox');

            userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });

            async function sendMessage() {
                const text = userInput.value.trim();
                if (!text) return;
                userInput.value = '';
                chatLog.innerHTML += <div style="margin-top: 8px; color: #a5f3fc;"><strong>You:</strong> </div>;
                chatLog.scrollTop = chatLog.scrollHeight;
                statusBox.innerText = 'Sarah is thinking...';

                try {
                    const res = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({text})
                    });
                    const data = await res.json();
                    statusBox.innerText = 'Call connected';
                    chatLog.innerHTML += <div style="margin-top: 8px; color: #38bdf8;"><strong>Sarah:</strong> </div>;
                    if (data.tools_called && data.tools_called.length > 0) {
                        data.tools_called.forEach(t => {
                            chatLog.innerHTML += <div style="margin: 4px 0 4px 12px; font-size: 11px; color: #4ade80;">⚙️ [Tool Executed: ]</div>;
                        });
                    }
                    chatLog.scrollTop = chatLog.scrollHeight;
                } catch (e) {
                    statusBox.innerText = 'Error connecting';
                }
            }
        </script>
    </body>
    </html>
    """

# --- Chat Simulation API ---
@app.post("/api/chat")
async def chat_turn(req: Request):
    data = await req.json()
    user_text = data.get("text", "")
    response = await engine.generate_response(user_text)
    return response

# --- Live Clinic Data Endpoints ---
@app.get("/api/clinic/appointments")
async def get_appointments():
    async with get_db_connection() as db:
        async with db.execute("SELECT confirmation_number, patient_name, date, time_slot, provider, phone, reason, status, created_at FROM appointments ORDER BY id DESC") as cursor:
            rows = await cursor.fetchall()
            return [{
                "confirmation_number": r[0],
                "patient_name": r[1],
                "date": r[2],
                "time_slot": r[3],
                "provider": r[4],
                "phone": r[5],
                "reason": r[6],
                "status": r[7],
                "created_at": r[8]
            } for r in rows]

@app.get("/api/clinic/refills")
async def get_refills():
    async with get_db_connection() as db:
        async with db.execute("SELECT refill_id, patient_name, medication, dosage, pharmacy_name, phone, status, created_at FROM refill_requests ORDER BY id DESC") as cursor:
            rows = await cursor.fetchall()
            return [{
                "refill_id": r[0],
                "patient_name": r[1],
                "medication": r[2],
                "dosage": r[3],
                "pharmacy_name": r[4],
                "phone": r[5],
                "status": r[6],
                "created_at": r[7]
            } for r in rows]

@app.get("/api/clinic/messages")
async def get_messages():
    async with get_db_connection() as db:
        async with db.execute("SELECT message_id, caller_name, phone_number, reason_for_call, message_body, status, created_at FROM general_messages ORDER BY id DESC") as cursor:
            rows = await cursor.fetchall()
            return [{
                "message_id": r[0],
                "caller_name": r[1],
                "phone_number": r[2],
                "reason_for_call": r[3],
                "message_body": r[4],
                "status": r[5],
                "created_at": r[6]
            } for r in rows]
