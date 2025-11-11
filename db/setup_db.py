# db/setup_db.py
"""
This script creates the SQLite database and applications table.
Run this once before using main.py
"""

import sqlite3
import os

# Ensure the data folder exists
os.makedirs("data", exist_ok=True)

# Path to the database file
DB_PATH = "data/job_tracker.db"

def create_db():
    # Connect to the database (creates file if it doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Create the applications table if it doesn't exist
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
    response_date TEXT,
    notes TEXT
)
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Database created at {DB_PATH}")

if __name__ == "__main__":
    create_db()
