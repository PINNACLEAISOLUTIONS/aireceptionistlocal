import os
import json
import asyncio
from typing import List, Dict, Any, AsyncGenerator
from clinical.prompt import PEDIATRIC_RECEPTIONIST_PROMPT, GREETING_MESSAGE
from clinical.tools import CLINICAL_TOOLS_SCHEMA, execute_clinical_tool

class ReceptionistVoiceEngine:
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY")
        self.model = os.getenv("LLM_MODEL", model)
        self.messages = [
            {"role": "system", "content": PEDIATRIC_RECEPTIONIST_PROMPT}
        ]

    def reset_conversation(self):
        self.messages = [
            {"role": "system", "content": PEDIATRIC_RECEPTIONIST_PROMPT}
        ]

    async def generate_response(self, user_text: str) -> Dict[str, Any]:
        """
        Processes user speech, coordinates tool calling, and generates Sarah's spoken response.
        """
        import httpx
        self.messages.append({"role": "user", "content": user_text})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": self.messages,
            "tools": CLINICAL_TOOLS_SCHEMA,
            "tool_choice": "auto",
            "temperature": 0.35
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
            if resp.status_code != 200:
                return {
                    "text": "I apologize, but I am experiencing a temporary connection issue. How can I help you with High Springs Pediatrics?",
                    "tools_called": []
                }
            
            data = resp.json()
            choice = data["choices"][0]["message"]
            tools_called = []

            if choice.get("tool_calls"):
                self.messages.append(choice)
                for tool_call in choice["tool_calls"]:
                    fn_name = tool_call["function"]["name"]
                    args = json.loads(tool_call["function"].get("arguments", "{}"))
                    tool_result_str = await execute_clinical_tool(fn_name, args)
                    tools_called.append({"name": fn_name, "arguments": args, "result": tool_result_str})

                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": fn_name,
                        "content": tool_result_str
                    })

                # Follow-up turn to generate natural voice response after tool execution
                follow_up_payload = {
                    "model": self.model,
                    "messages": self.messages,
                    "temperature": 0.35
                }
                follow_resp = await client.post("https://api.openai.com/v1/chat/completions", json=follow_up_payload, headers=headers)
                final_msg = follow_resp.json()["choices"][0]["message"]["content"]
                self.messages.append({"role": "assistant", "content": final_msg})
                return {"text": final_msg, "tools_called": tools_called}
            else:
                final_msg = choice.get("content", "")
                self.messages.append({"role": "assistant", "content": final_msg})
                return {"text": final_msg, "tools_called": []}

    async def text_to_speech_elevenlabs(self, text: str) -> bytes:
        """
        Synthesizes Sarah's voice via ElevenLabs API using eleven_flash_v2.
        """
        import httpx
        eleven_key = os.getenv("ELEVENLABS_API_KEY")
        voice_id = os.getenv("ELEVENLABS_VOICE_ID", "sarah")
        if not eleven_key:
            return b""

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": eleven_key,
            "Content-Type": "application/json"
        }
        body = {
            "text": text,
            "model_id": "eleven_flash_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=body, headers=headers)
            if resp.status_code == 200:
                return resp.content
            return b""
