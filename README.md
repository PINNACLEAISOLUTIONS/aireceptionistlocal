# 🩺 High Springs Pediatrics — Autonomous AI Voice Receptionist
### *Self-Hosted Telephony Gateway & Clinical Triage Engine*

[![Pinnacle AI Solutions](https://img.shields.io/badge/Engineered%20by-Pinnacle%20AI%20Solutions-6366f1.svg)]()
[![Client](https://img.shields.io/badge/Client-High%20Springs%20Pediatrics-0ea5e9.svg)]()
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![Telnyx SIP](https://img.shields.io/badge/Telephony-Telnyx%20Dedicated%20SIP-green.svg)](https://telnyx.com)
[![Voice Pipeline](https://img.shields.io/badge/Voice-Deepgram%20%7C%20ElevenLabs-f59e0b.svg)]()
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()

> **Client:** High Springs Pediatrics and Primary Care  
> **Physician & Medical Director:** Dr. Nasir Ahmed, M.D.  
> **Location:** 19228 NW US Highway 441, High Springs, FL 32643  
> **Dedicated Inbound Clinic Line:** +1 (386) 639-0334  
> **Engineering Firm:** Pinnacle AI Solutions  

---

## 🌟 Executive Overview & Architectural Portfolio

This repository houses the next-generation, self-hosted AI voice receptionist engineered by **Pinnacle AI Solutions** for **High Springs Pediatrics and Primary Care**.

Previously, the clinic's phone system relied on third-party SaaS voice orchestrators (such as Vapi.ai) which charged recurring per-minute cloud markups, routed patient audio through third-party servers, and added latency.

**The Pinnacle Architecture** migrates the clinic to an independent, carrier-direct self-hosted telephony stack powered by **Tel-Agent** and **Telnyx SIP/TeXML**:
- **Direct Carrier Ingress:** Incoming patient calls hit our dedicated Florida telephone number (+1 (386) 639-0334) and stream directly to our self-hosted voice gateway.
- **Zero Third-Party SaaS Markups:** Cuts operating telecom overhead by over 80% while retaining full data privacy, HIPAA compliance, and local database control.
- **Ultra-Realistic Voice & Interruption Handling:** Powered by ElevenLabs *"Sarah"* voice synthesis (leven_flash_v2), Deepgram real-time transcription, and sub-800ms streaming turn-taking with immediate barge-in capability.

---

## 📋 Clinical Capabilities & Autonomous Tool Execution

Sarah operates under strict clinical protocol as an autonomous front-desk medical receptionist:

| Clinical Tool | Purpose & Patient Interaction | Telephony Output |
| :--- | :--- | :--- |
| check_availability | Queries open clinic consultation slots by date, doctor, or visit type (well-child check, sick visit, sports physical). | Returns available 30-min slots (9:30 AM, 10:15 AM, 2:00 PM, 3:45 PM). |
| ook_appointment | Captures patient name, DOB, guardian, contact phone, date, and reason. Persists record to SQLite database. | Issues unique 3-digit confirmation number read out loud with natural spacing: *"Your confirmation number is 7 4 2."* |
| efill_request | Collects prescription name, dosage, preferred pharmacy, and patient DOB for clinical nursing triage. | Logs request (REF-XXXXX) into the nursing triage queue with 24-48 hr notice. |
| 	ake_general_message | Captures non-urgent inquiries, billing questions, or office notes. | Securely routes ticket (MSG-XXXXX) to front-office administrative staff. |

### 🛡️ Clinical & Safety Guardrails
- **Emergency Protocol:** If a caller mentions severe, life-threatening symptoms (e.g. respiratory distress, cyanosis, severe trauma), Sarah immediately triggers the medical emergency override:
  > *"If the patient is experiencing a life-threatening medical emergency, please hang up and call 911 or proceed to the nearest emergency room immediately."*
- **Non-Physician Boundary:** Never attempts medical diagnosis or alteration of prescribed dosages.
- **HIPAA Privacy:** All patient identifiers and consultation records remain in the clinic's isolated local database.

---

## 🔑 Required API Keys & Environment Configuration

To keep production credentials secure, this repository strictly ignores .env files (.gitignore). Create a local .env file using the provided .env.example template:

`ash
cp .env.example .env
`

### Key Reference Table:
| Environment Variable | Service | Description |
| :--- | :--- | :--- |
| TELNYX_API_KEY | [Telnyx](https://telnyx.com) | Direct SIP and TeXML carrier authentication for inbound call handling on +1 (386) 639-0334. |
| TELNYX_PHONE_NUMBER | Telnyx | Dedicated clinic line: +13866390334. |
| OPENAI_API_KEY | OpenAI / Groq | Powers Sarah's clinical reasoning and function calling (gpt-4o-mini). |
| DEEPGRAM_API_KEY | Deepgram | Low-latency streaming speech-to-text (STT) for phone audio. |
| ELEVENLABS_API_KEY | ElevenLabs | Generates Sarah's warm, professional voice using leven_flash_v2. |
| ELEVENLABS_VOICE_ID| ElevenLabs | Voice ID (Defaults to sarah). |
| DATABASE_PATH | Local SQLite | Path to persistent storage (Default: clinic.db). |

---

## ⚡ Quick Start & Verification

### 1. Install Dependencies
Ensure Python 3.11+ is installed:
`powershell
pip install -r requirements.txt
`

### 2. Run Automated Test Suite
Execute the full clinical and telephony verification suite:
`powershell
python run_tests.py
`
*Validates database schema creation, slot queries, appointment booking with 3-digit confirmation codes, refill triage, messaging, and Tel-Agent tool bindings.*

### 3. Launch Inbound Voice Gateway & Browser Call Simulator
`powershell
uvicorn telephony.sip_inbound:app --host 0.0.0.0 --port 8000 --reload
`

- **Interactive Voice Tester:** Open [http://localhost:8000/call](http://localhost:8000/call) to converse with Sarah directly in your browser.
- **Telnyx Webhook:** Point your Telnyx TeXML Application voice URL to https://<your-domain-or-tunnel>/api/telephony/telnyx/inbound.
- **Live Clinic Records:**
  - Appointments: GET /api/clinic/appointments
  - Refill Requests: GET /api/clinic/refills
  - Office Messages: GET /api/clinic/messages

---

## 🏢 Engineered by Pinnacle AI Solutions
*Architecting enterprise autonomous AI agents, clinical voice triage systems, and self-hosted telephony infrastructure.*
