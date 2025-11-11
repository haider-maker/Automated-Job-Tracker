# db/db_functions.py

import sqlite3
from datetime import datetime

DB_PATH = "data/job_tracker.db"

# -----------------------------
# Create table if it doesn't exist
# -----------------------------
def init_db(db_path=DB_PATH):
    """
    Initialize the applications table with necessary columns:
    - application_status: default 'Applied'
    """
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
        notes TEXT
    )
    """)
    conn.commit()
    conn.close()


# -----------------------------
# Insert a single application
# -----------------------------
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
    """
    Insert a single job application into the DB.
    """
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


# -----------------------------
# Check if a job already exists
# -----------------------------
def job_already_processed(job_url, db_path=DB_PATH):
    """
    Returns True if job_url already exists in the DB.
    """
    if not job_url:
        return False
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM applications WHERE job_url = ?", (job_url,))
    result = cur.fetchone()
    conn.close()
    return result is not None


# -----------------------------
# Batch insert applications
# -----------------------------
def add_applications_batch(applications, db_path=DB_PATH):
    """
    Batch insert a list of applications.
    Each application should be a dict with:
    - date_applied
    - platform
    - company
    - position
    - job_url
    - application_status (default 'Applied')
    - notes
    """
    if not applications:
        print("⚠️ No new applications to insert.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    to_insert = []
    for app in applications:
        cursor.execute("SELECT 1 FROM applications WHERE job_url = ?", (app["job_url"],))
        if cursor.fetchone() is None:
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
        cursor.executemany("""
            INSERT INTO applications 
            (date_applied, platform, company, position, job_url, application_status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, to_insert)
        conn.commit()
        print(f"✅ Batch inserted {len(to_insert)} new applications.")
    else:
        print("ℹ️ No new unique applications found.")

    conn.close()
