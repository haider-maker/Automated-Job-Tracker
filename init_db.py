import sqlite3
import os

DB_PATH = "data/job_tracker.db"

# Ensure directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id TEXT UNIQUE,
    date_applied TEXT,
    platform TEXT,
    company TEXT,
    position TEXT,
    job_url TEXT,
    application_status TEXT,
    notes TEXT
)
""")

conn.commit()
conn.close()

print("✅ Database initialized successfully at", DB_PATH)
