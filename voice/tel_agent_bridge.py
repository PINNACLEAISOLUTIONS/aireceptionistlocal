"""
Tel-Agent Native Bridge:
Wraps High Springs Pediatrics clinical tools into Tel-Agent Tool instances.
"""
from typing import List
from agent.tools.base import Tool
from clinical.tools import (
    handle_check_availability,
    handle_book_appointment,
    handle_refill_request,
    handle_take_general_message
)

def get_pinnacle_clinical_tools() -> List[Tool]:
    """
    Returns the list of Tel-Agent compatible tools ready to plug into Tel-Agent's voice session loop.
    """
    return [
        Tool(
            name="check_availability",
            description="Queries available appointment slots at High Springs Pediatrics for a given date and visit type.",
            parameters={
                "type": "object",
                "properties": {
                    "date": {"type": "string", "description": "Requested date or day (e.g. tomorrow, Friday, 2026-09-18)"},
                    "visitType": {"type": "string", "description": "Reason or visit type (e.g. Sick visit, Well child check)"},
                    "provider": {"type": "string", "description": "Doctor name (Dr. Nasir Ahmed or Dr. Ramin Ahmed)"}
                },
                "required": ["date"]
            },
            run=handle_check_availability
        ),
        Tool(
            name="book_appointment",
            description="Reserves an appointment, records patient details into the clinic database, and generates a 3-digit confirmation number.",
            parameters={
                "type": "object",
                "properties": {
                    "patientName": {"type": "string", "description": "Full name of the child/patient receiving care."},
                    "parentName": {"type": "string", "description": "Name of the parent or guardian accompanying the child."},
                    "phone": {"type": "string", "description": "Contact phone number for confirmation."},
                    "dob": {"type": "string", "description": "Patient date of birth."},
                    "date": {"type": "string", "description": "Confirmed date of the appointment."},
                    "timeSlot": {"type": "string", "description": "Selected time slot (e.g. 10:15 AM, 2:45 PM)."},
                    "reason": {"type": "string", "description": "Clinical reason for visit."}
                },
                "required": ["patientName", "date", "timeSlot"]
            },
            run=handle_book_appointment
        ),
        Tool(
            name="refill_request",
            description="Logs a prescription refill request for nursing triage review.",
            parameters={
                "type": "object",
                "properties": {
                    "patientName": {"type": "string", "description": "Full legal name of the patient."},
                    "dob": {"type": "string", "description": "Patient date of birth."},
                    "medication": {"type": "string", "description": "Name of the medication requested."},
                    "dosage": {"type": "string", "description": "Dosage/strength if known."},
                    "pharmacyName": {"type": "string", "description": "Preferred pharmacy name and location."},
                    "phone": {"type": "string", "description": "Callback phone number."}
                },
                "required": ["patientName", "medication"]
            },
            run=handle_refill_request
        ),
        Tool(
            name="take_general_message",
            description="Logs a general caller message routed directly to the clinic front desk staff.",
            parameters={
                "type": "object",
                "properties": {
                    "callerName": {"type": "string", "description": "Name of the caller."},
                    "phoneNumber": {"type": "string", "description": "Callback phone number."},
                    "reasonForCall": {"type": "string", "description": "Brief subject of the message."},
                    "messageBody": {"type": "string", "description": "Full detailed message text."}
                },
                "required": ["callerName", "messageBody"]
            },
            run=handle_take_general_message
        )
    ]
