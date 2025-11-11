import sqlite3
import pandas as pd
from tabulate import tabulate
from pathlib import Path

# Define DB path (same as in db_functions.py)
DB_PATH = Path("data/job_tracker.db")

def view_applications(limit=500, show_incomplete=True):
    """View job applications stored in the database in a clean table format."""
    if not DB_PATH.exists():
        print(f"⚠️ Database not found at {DB_PATH}. Please run the tracker or API first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get table columns dynamically
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
        print("⚠️ No recognizable columns found in 'applications' table.")
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
        print("⚠️ No job applications found in the database.")
        return

    # Clean long URLs
    if "job_url" in df.columns:
        df["job_url"] = df["job_url"].apply(
            lambda u: u[:60] + "..." if isinstance(u, str) and len(u) > 60 else u
        )

    # Filter incomplete entries if requested
    if not show_incomplete:
        df = df[df["company"].str.strip() != ""]
        df = df[df["position"].str.strip() != ""]

    # Replace blanks with “—”
    df = df.fillna("—")
    df.replace("", "—", inplace=True)

    print(f"📊 Showing {len(df)} recent applications (limit={limit})\n")
    print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))

if __name__ == "__main__":
    print("📊 Viewing job applications from database...\n")
    view_applications(limit=1000, show_incomplete=True)
