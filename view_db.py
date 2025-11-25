import sqlite3
import pandas as pd
from tabulate import tabulate
from pathlib import Path
import json
import os

# --------------------------------------------------
# Load config.json for consistent DB path
# --------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]     # /Job_Tracker
CREDS_DIR = ROOT_DIR / "creds"
CONFIG_PATH = CREDS_DIR / "config.json"

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

DB_PATH = Path(config["DB_PATH"])   # absolute or relative stored in config
print(f"Using DB: {DB_PATH}")

# --------------------------------------------------
# View Applications
# --------------------------------------------------
def view_applications(limit=5, show_incomplete=True):
    if not DB_PATH.exists():
        print(f"⚠️ Database not found at {DB_PATH}.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(applications);")
    columns = [col[1] for col in cursor.fetchall()]

    wanted_cols = [
        col for col in [
            "id", "date_applied", "platform", "company",
            "position", "job_url", "application_status",
            "email_id", "notes"
        ] if col in columns
    ]

    if not wanted_cols:
        print("⚠️ No recognizable columns found in applications table.")
        conn.close()
        return

    query = f"""
        SELECT {', '.join(wanted_cols)}
        FROM applications
        ORDER BY date_applied DESC
        LIMIT ?;
    """

    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()

    if df.empty:
        print("⚠️ No job applications found.")
        return

    if "job_url" in df.columns:
        df["job_url"] = df["job_url"].apply(
            lambda u: u[:60] + "..." if isinstance(u, str) and len(u) > 60 else u
        )

    if not show_incomplete:
        df = df[df["company"].str.strip() != ""]
        df = df[df["position"].str.strip() != ""]

    df = df.fillna("—")
    df.replace("", "—", inplace=True)

    print(f"📊 Showing {len(df)} recent applications (limit={limit})\n")
    print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))


if __name__ == "__main__":
    print("📊 Viewing job applications...\n")
    view_applications(limit=5, show_incomplete=True)
