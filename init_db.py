import sqlite3
from pathlib import Path

# -----------------------------------------------------
# Correct DB path using project structure
# -----------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent          # Automated-Job-Tracker
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "job_tracker.db"

# Ensure /data folder exists
DATA_DIR.mkdir(exist_ok=True)

# Initialize DB
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
    notes TEXT
)
""")

conn.commit()
conn.close()

print("✅ Database initialized successfully at", DB_PATH)
