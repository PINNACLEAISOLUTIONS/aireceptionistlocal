import asyncio
import json
import pytest
import os
import aiosqlite

from database.db import init_db, get_db_connection
from clinical.tools import (
    handle_check_availability,
    handle_book_appointment,
    handle_refill_request,
    handle_take_general_message,
    execute_clinical_tool
)
from voice.tel_agent_bridge import get_pinnacle_clinical_tools

TEST_DB = "test_clinic.db"

@pytest.fixture(autouse=True)
def setup_test_db():
    os.environ["DATABASE_PATH"] = TEST_DB
    asyncio.run(init_db(TEST_DB))
    yield
    if os.path.exists(TEST_DB):
        try:
            os.remove(TEST_DB)
        except Exception:
            pass

@pytest.mark.asyncio
async def test_check_availability():
    res = await handle_check_availability({"date": "tomorrow", "visitType": "Sick Visit"})
    data = json.loads(res)
    assert data["status"] == "success"
    assert "Dr. Nasir Ahmed, M.D." in data["provider"]
    assert len(data["available_slots"]) > 0

@pytest.mark.asyncio
async def test_book_appointment():
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
    assert "Liam Martinez" in data["spoken_message"]

    # Verify database persistence
    async with await get_db_connection(TEST_DB) as db:
        async with db.execute("SELECT patient_name, confirmation_number, status FROM appointments WHERE patient_name = 'Liam Martinez'") as cursor:
            row = await cursor.fetchone()
            assert row is not None
            assert row[0] == "Liam Martinez"
            assert row[1] == data["confirmation_number"]
            assert row[2] == "CONFIRMED"

@pytest.mark.asyncio
async def test_refill_request():
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

    # Verify database persistence
    async with await get_db_connection(TEST_DB) as db:
        async with db.execute("SELECT patient_name, medication, status FROM refill_requests WHERE patient_name = 'Sophia Johnson'") as cursor:
            row = await cursor.fetchone()
            assert row is not None
            assert row[0] == "Sophia Johnson"
            assert row[1] == "Amoxicillin 250mg/5ml"

@pytest.mark.asyncio
async def test_take_general_message():
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

    # Verify database persistence
    async with await get_db_connection(TEST_DB) as db:
        async with db.execute("SELECT caller_name, reason_for_call FROM general_messages WHERE caller_name = 'Marcus Bell'") as cursor:
            row = await cursor.fetchone()
            assert row is not None
            assert row[0] == "Marcus Bell"

def test_tel_agent_tools_bridge():
    tools = get_pinnacle_clinical_tools()
    assert len(tools) == 4
    tool_names = [t.name for t in tools]
    assert "check_availability" in tool_names
    assert "book_appointment" in tool_names
    assert "refill_request" in tool_names
    assert "take_general_message" in tool_names
