# db/db_functions.py

import sqlite3
from datetime import datetime
from pathlib import Path

# -----------------------------------------------------
# Correct DB path (matches entire project)
# -----------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent    # Automated-Job-Tracker
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "job_tracker.db"


# -----------------------------------------------------
# Initialize DB + table
# -----------------------------------------------------
def init_db(db_path=DB_PATH):
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_url TEXT UNIQUE,
            date_applied TEXT,
            platform TEXT,
            company TEXT,
            position TEXT,
            application_status TEXT DEFAULT 'Applied',
            notes TEXT,
            email_id TEXT
        )
    """)
    conn.commit()
    conn.close()


# -----------------------------------------------------
# Insert a single record
# -----------------------------------------------------
def add_application(
    date_applied,
    platform,
    company,
    position,
    job_url=None,
    notes="",
    application_status="Applied",
    db_path=DB_PATH
):
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("""
        INSERT OR IGNORE INTO applications 
        (date_applied, platform, company, position, job_url, application_status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        date_applied.isoformat() if isinstance(date_applied, datetime) else date_applied,
        platform,
        company,
        position,
        job_url,
        application_status,
        notes
    ))
    conn.commit()
    conn.close()


# -----------------------------------------------------
# Check if job URL already exists
# -----------------------------------------------------
def job_already_processed(job_url, db_path=DB_PATH):
    if not job_url:
        return False
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM applications WHERE job_url = ?", (job_url,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists


# -----------------------------------------------------
# Batch Insert
# -----------------------------------------------------
def add_applications_batch(applications, db_path=DB_PATH):
    if not applications:
        print("⚠️ No new applications to insert.")
        return

    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    to_insert = []

    for app in applications:
        cur.execute("SELECT 1 FROM applications WHERE job_url = ?", (app["job_url"],))
        if cur.fetchone() is None:
            to_insert.append((
                app.get("date_applied"),
                app.get("platform"),
                app.get("company"),
                app.get("position"),
                app.get("job_url"),
                app.get("application_status", "Applied"),
                app.get("notes", "")
            ))

    if to_insert:
        cur.executemany("""
            INSERT INTO applications 
            (date_applied, platform, company, position, job_url, application_status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, to_insert)
        conn.commit()
        print(f"✅ Batch inserted {len(to_insert)} applications.")
    else:
        print("ℹ️ No unique applications found.")

    conn.close()
