import json
from typing import Dict, Any
from database.db import create_appointment, create_refill_request, create_general_message

# OpenAI / Anthropic Tool Definitions for LLM function calling
CLINICAL_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Queries available appointment slots at High Springs Pediatrics based on requested date and visit type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Requested date or day (e.g., 'tomorrow', 'Friday', '2026-09-18')"
                    },
                    "visitType": {
                        "type": "string",
                        "description": "Reason or visit type, e.g. 'Sick visit', 'Well child check', 'Immunizations', 'Sports physical'"
                    },
                    "provider": {
                        "type": "string",
                        "description": "Doctor name if specified by caller, e.g., 'Dr. Nasir Ahmed' or 'Dr. Ramin Ahmed'"
                    }
                },
                "required": ["date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Reserves an appointment, records patient details into the clinic database, and generates a 3-digit confirmation number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patientName": {
                        "type": "string",
                        "description": "Full name of the child/patient receiving care."
                    },
                    "parentName": {
                        "type": "string",
                        "description": "Name of the parent or guardian accompanying the child."
                    },
                    "phone": {
                        "type": "string",
                        "description": "Best contact phone number for SMS confirmation."
                    },
                    "dob": {
                        "type": "string",
                        "description": "Patient date of birth (e.g. '04/12/2018')."
                    },
                    "date": {
                        "type": "string",
                        "description": "Confirmed date of the appointment."
                    },
                    "timeSlot": {
                        "type": "string",
                        "description": "Selected time slot (e.g., '10:15 AM', '2:45 PM')."
                    },
                    "reason": {
                        "type": "string",
                        "description": "Brief clinical reason for visit."
                    },
                    "doctor": {
                        "type": "string",
                        "description": "Requested physician: Dr. Nasir Ahmed or Dr. Ramin Ahmed."
                    }
                },
                "required": ["patientName", "date", "timeSlot"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "refill_request",
            "description": "Logs a prescription refill request for nursing triage review.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patientName": {
                        "type": "string",
                        "description": "Full legal name of the patient."
                    },
                    "dob": {
                        "type": "string",
                        "description": "Patient date of birth."
                    },
                    "medication": {
                        "type": "string",
                        "description": "Name of the medication requested."
                    },
                    "dosage": {
                        "type": "string",
                        "description": "Dosage/strength if known (e.g., '10mg daily', 'liquid amoxicillin')."
                    },
                    "pharmacyName": {
                        "type": "string",
                        "description": "Preferred pharmacy name and location (e.g., 'Walgreens High Springs')."
                    },
                    "phone": {
                        "type": "string",
                        "description": "Callback phone number."
                    }
                },
                "required": ["patientName", "medication"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "take_general_message",
            "description": "Logs a general caller message routed directly to the clinic front desk staff.",
            "parameters": {
                "type": "object",
                "properties": {
                    "callerName": {
                        "type": "string",
                        "description": "Name of the caller."
                    },
                    "phoneNumber": {
                        "type": "string",
                        "description": "Callback phone number."
                    },
                    "reasonForCall": {
                        "type": "string",
                        "description": "Brief subject of the message."
                    },
                    "messageBody": {
                        "type": "string",
                        "description": "Full detailed message text."
                    }
                },
                "required": ["callerName", "messageBody"]
            }
        }
    }
]

async def handle_check_availability(args: Dict[str, Any]) -> str:
    date = args.get("date", "tomorrow")
    visit_type = args.get("visitType", "Pediatric Consultation")
    provider = args.get("provider", "Dr. Nasir Ahmed, M.D.")
    
    if "ramin" in provider.lower():
        provider = "Dr. Ramin Ahmed, M.D."
    else:
        provider = "Dr. Nasir Ahmed, M.D."
        
    slots = ["9:30 AM", "10:15 AM", "11:15 AM", "2:00 PM", "2:45 PM", "3:45 PM"]
    return json.dumps({
        "status": "success",
        "provider": provider,
        "date": date,
        "visit_type": visit_type,
        "available_slots": slots,
        "spoken_message": f"{provider} has open slots for a {visit_type} on {date} at 9:30 AM, 10:15 AM, 11:15 AM, 2:00 PM, and 3:45 PM."
    })

async def handle_book_appointment(args: Dict[str, Any]) -> str:
    patient_name = args.get("patientName", "Patient")
    parent_name = args.get("parentName", "Parent/Guardian")
    phone = args.get("phone", "Not provided")
    dob = args.get("dob", "Not specified")
    date = args.get("date", "Scheduled Date")
    time_slot = args.get("timeSlot", "10:00 AM")
    reason = args.get("reason", "Pediatric Visit")
    
    doctor_pick = args.get("doctor", "Dr. Nasir Ahmed, M.D.")
    provider = "Dr. Ramin Ahmed, M.D." if "ramin" in str(doctor_pick).lower() else "Dr. Nasir Ahmed, M.D."
    
    booking = await create_appointment(
        patient_name=patient_name,
        date=date,
        time_slot=time_slot,
        parent_name=parent_name,
        phone=phone,
        dob=dob,
        provider=provider,
        reason=reason
    )
    
    conf_digits = " ".join(list(booking["confirmation_number"]))
    return json.dumps({
        "status": "confirmed",
        "confirmation_number": booking["confirmation_number"],
        "patient_name": patient_name,
        "date": date,
        "time_slot": time_slot,
        "provider": provider,
        "spoken_message": f"You're all set! Appointment booked for {patient_name} on {date} at {time_slot}. Your confirmation number is {conf_digits}. Is there anything else I can help you with today?"
    })

async def handle_refill_request(args: Dict[str, Any]) -> str:
    patient_name = args.get("patientName", "Patient")
    medication = args.get("medication", "Prescription")
    dob = args.get("dob", "Not specified")
    phone = args.get("phone", "Not provided")
    dosage = args.get("dosage", "Standard Dosage")
    pharmacy = args.get("pharmacyName", "Pharmacy on file")
    
    result = await create_refill_request(
        patient_name=patient_name,
        medication=medication,
        dob=dob,
        phone=phone,
        dosage=dosage,
        pharmacy_name=pharmacy
    )
    
    return json.dumps({
        "status": "success",
        "refill_id": result["refill_id"],
        "spoken_message": f"The refill request for {medication} for {patient_name} has been securely submitted to our clinical nursing triage. Please allow 24 to 48 business hours for review."
    })

async def handle_take_general_message(args: Dict[str, Any]) -> str:
    caller_name = args.get("callerName", "Caller")
    phone = args.get("phoneNumber", "Not provided")
    reason = args.get("reasonForCall", "General Inquiry")
    body = args.get("messageBody", "No message details provided")
    
    result = await create_general_message(
        caller_name=caller_name,
        phone_number=phone,
        reason_for_call=reason,
        message_body=body
    )
    
    return json.dumps({
        "status": "success",
        "message_id": result["message_id"],
        "spoken_message": f"Thank you {caller_name}, your message regarding {reason} has been securely logged and routed to the High Springs office staff."
    })

async def execute_clinical_tool(tool_name: str, arguments: Dict[str, Any]) -> str:
    if tool_name == "check_availability":
        return await handle_check_availability(arguments)
    elif tool_name == "book_appointment":
        return await handle_book_appointment(arguments)
    elif tool_name == "refill_request":
        return await handle_refill_request(arguments)
    elif tool_name == "take_general_message":
        return await handle_take_general_message(arguments)
    else:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
