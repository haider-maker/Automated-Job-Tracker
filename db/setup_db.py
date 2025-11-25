# db/setup_db.py

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent   # Automated-Job-Tracker
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "job_tracker.db"


def create_db():
    DATA_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id TEXT,
            date_applied TEXT,
            platform TEXT,
            company TEXT,
            position TEXT,
            job_url TEXT UNIQUE,
            application_status TEXT,
            response_date TEXT,
            notes TEXT
        )
    """)

    conn.commit()
    conn.close()
    print(f"✅ Database created at: {DB_PATH}")


if __name__ == "__main__":
    create_db()
