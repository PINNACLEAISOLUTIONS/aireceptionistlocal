import asyncio
import json
import os
import uuid
from database.db import init_db, get_db_connection
from clinical.tools import (
    handle_check_availability,
    handle_book_appointment,
    handle_refill_request,
    handle_take_general_message,
    execute_clinical_tool
)
from voice.tel_agent_bridge import get_pinnacle_clinical_tools

TEST_DB = f"test_clinic_{uuid.uuid4().hex[:6]}.db"

async def run_all_tests():
    print("--- 1. Testing Database Initialization ---")
    os.environ["DATABASE_PATH"] = TEST_DB
    await init_db(TEST_DB)
    print("✓ Database initialized successfully.")

    print("\n--- 2. Testing Tool: check_availability ---")
    res = await handle_check_availability({"date": "tomorrow", "visitType": "Sick Visit"})
    data = json.loads(res)
    assert data["status"] == "success"
    assert "Dr. Nasir Ahmed, M.D." in data["provider"]
    assert len(data["available_slots"]) > 0
    print(f"✓ Available slots verified: {data['available_slots']}")

    print("\n--- 3. Testing Tool: book_appointment ---")
    args = {
        "patientName": "Liam Martinez",
        "parentName": "Elena Martinez",
        "phone": "386-555-0199",
        "dob": "08/14/2019",
        "date": "2026-09-20",
        "timeSlot": "10:15 AM",
        "reason": "Ear pain"
    }
    res = await handle_book_appointment(args)
    data = json.loads(res)
    assert data["status"] == "confirmed"
    assert len(data["confirmation_number"]) == 3
    assert data["confirmation_number"].isdigit()
    print(f"✓ Appointment booked! Conf #: {data['confirmation_number']}")
    print(f"✓ Spoken read-back: {data['spoken_message']}")

    # Verify database persistence
    async with get_db_connection(TEST_DB) as db:
        async with db.execute("SELECT patient_name, confirmation_number, status FROM appointments WHERE patient_name = 'Liam Martinez'") as cursor:
            row = await cursor.fetchone()
            assert row is not None
            assert row[0] == "Liam Martinez"
            assert row[1] == data["confirmation_number"]
            print(f"✓ Database verified record: {row[0]}, Conf: {row[1]}, Status: {row[2]}")

    print("\n--- 4. Testing Tool: refill_request ---")
    args = {
        "patientName": "Sophia Johnson",
        "medication": "Amoxicillin 250mg/5ml",
        "pharmacyName": "CVS High Springs",
        "phone": "386-555-0144"
    }
    res = await handle_refill_request(args)
    data = json.loads(res)
    assert data["status"] == "success"
    assert data["refill_id"].startswith("REF-")
    print(f"✓ Refill logged: {data['refill_id']}")

    async with get_db_connection(TEST_DB) as db:
        async with db.execute("SELECT patient_name, medication, status FROM refill_requests WHERE patient_name = 'Sophia Johnson'") as cursor:
            row = await cursor.fetchone()
            assert row is not None
            assert row[0] == "Sophia Johnson"

    print("\n--- 5. Testing Tool: take_general_message ---")
    args = {
        "callerName": "Marcus Bell",
        "phoneNumber": "386-555-0188",
        "reasonForCall": "Insurance question",
        "messageBody": "Do you accept Florida Healthy Kids?"
    }
    res = await handle_take_general_message(args)
    data = json.loads(res)
    assert data["status"] == "success"
    assert data["message_id"].startswith("MSG-")
    print(f"✓ Message logged: {data['message_id']}")

    async with get_db_connection(TEST_DB) as db:
        async with db.execute("SELECT caller_name, reason_for_call FROM general_messages WHERE caller_name = 'Marcus Bell'") as cursor:
            row = await cursor.fetchone()
            assert row is not None
            assert row[0] == "Marcus Bell"

    print("\n--- 6. Testing Tel-Agent Native Bridge ---")
    tools = get_pinnacle_clinical_tools()
    assert len(tools) == 4
    tool_names = [t.name for t in tools]
    print(f"✓ Tel-Agent tools registered: {tool_names}")

    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except Exception:
            pass

    print("\n==========================================")
    print("🎉 ALL 6 CLINICAL & TELEPHONY TESTS PASSED!")
    print("==========================================")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
