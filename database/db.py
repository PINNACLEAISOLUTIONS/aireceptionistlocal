import aiosqlite
import os
import random
from datetime import datetime

def get_db_path(custom_path: str = None) -> str:
    return custom_path or os.getenv("DATABASE_PATH", "clinic.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    confirmation_number TEXT NOT NULL UNIQUE,
    patient_name TEXT NOT NULL,
    parent_name TEXT,
    phone TEXT,
    dob TEXT,
    provider TEXT DEFAULT 'Dr. Nasir Ahmed, M.D.',
    date TEXT NOT NULL,
    time_slot TEXT NOT NULL,
    reason TEXT,
    status TEXT DEFAULT 'CONFIRMED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS refill_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    refill_id TEXT NOT NULL UNIQUE,
    patient_name TEXT NOT NULL,
    dob TEXT,
    phone TEXT,
    medication TEXT NOT NULL,
    dosage TEXT,
    pharmacy_name TEXT,
    status TEXT DEFAULT 'TRIAGE_DASHBOARD_LOGGED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS general_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id TEXT NOT NULL UNIQUE,
    caller_name TEXT NOT NULL,
    phone_number TEXT,
    reason_for_call TEXT,
    message_body TEXT,
    status TEXT DEFAULT 'ROUTED_TO_OFFICE_STAFF',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def get_db_connection(db_path: str = None):
    return aiosqlite.connect(get_db_path(db_path))

async def init_db(db_path: str = None):
    actual_path = get_db_path(db_path)
    async with aiosqlite.connect(actual_path) as db:
        await db.executescript(SCHEMA_SQL)
        await db.commit()

async def create_appointment(
    patient_name: str,
    date: str,
    time_slot: str,
    parent_name: str = "Parent/Guardian",
    phone: str = "Not provided",
    dob: str = "Not specified",
    provider: str = "Dr. Nasir Ahmed, M.D.",
    reason: str = "Routine Pediatric Visit",
    db_path: str = None
) -> dict:
    conf_number = str(random.randint(100, 999))
    actual_path = get_db_path(db_path)
    async with aiosqlite.connect(actual_path) as db:
        await db.execute(
            """
            INSERT INTO appointments (confirmation_number, patient_name, parent_name, phone, dob, provider, date, time_slot, reason, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'CONFIRMED')
            """,
            (conf_number, patient_name, parent_name, phone, dob, provider, date, time_slot, reason)
        )
        await db.commit()
    return {
        "status": "confirmed",
        "confirmation_number": conf_number,
        "patient_name": patient_name,
        "date": date,
        "time_slot": time_slot,
        "provider": provider
    }

async def create_refill_request(
    patient_name: str,
    medication: str,
    dob: str = "Not specified",
    phone: str = "Not provided",
    dosage: str = "Standard Prescription",
    pharmacy_name: str = "Pharmacy on file",
    db_path: str = None
) -> dict:
    refill_id = f"REF-{random.randint(10000, 99999)}"
    actual_path = get_db_path(db_path)
    async with aiosqlite.connect(actual_path) as db:
        await db.execute(
            """
            INSERT INTO refill_requests (refill_id, patient_name, dob, phone, medication, dosage, pharmacy_name, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'TRIAGE_DASHBOARD_LOGGED')
            """,
            (refill_id, patient_name, dob, phone, medication, dosage, pharmacy_name)
        )
        await db.commit()
    return {
        "status": "success",
        "refill_id": refill_id,
        "patient_name": patient_name,
        "medication": medication
    }

async def create_general_message(
    caller_name: str,
    phone_number: str = "Not provided",
    reason_for_call: str = "General Inquiry",
    message_body: str = "No message",
    db_path: str = None
) -> dict:
    message_id = f"MSG-{random.randint(10000, 99999)}"
    actual_path = get_db_path(db_path)
    async with aiosqlite.connect(actual_path) as db:
        await db.execute(
            """
            INSERT INTO general_messages (message_id, caller_name, phone_number, reason_for_call, message_body, status)
            VALUES (?, ?, ?, ?, ?, 'ROUTED_TO_OFFICE_STAFF')
            """,
            (message_id, caller_name, phone_number, reason_for_call, message_body)
        )
        await db.commit()
    return {
        "status": "success",
        "message_id": message_id,
        "caller_name": caller_name,
        "reason_for_call": reason_for_call
    }
