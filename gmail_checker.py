from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import sqlite3
import os
import re
import json
from datetime import datetime

# -----------------------------
# Paths Setup
# -----------------------------
# Current script directory: Automated-Job-Tracker
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Root project directory: Job_Tracker
ROOT_DIR = os.path.dirname(BASE_DIR)

# Path to creds folder
CREDS_DIR = os.path.join(ROOT_DIR, "creds")

# Load config.json from creds folder
CONFIG_PATH = os.path.join(CREDS_DIR, "config.json")
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

# Database path (fallback to data/job_tracker.db)
DB_PATH = config.get("DB_PATH", os.path.join(BASE_DIR, "data", "job_tracker.db"))

# Paths to credentials.json and token.json
CREDENTIALS_PATH = os.path.join(CREDS_DIR, "credentials.json")
TOKEN_PATH = os.path.join(CREDS_DIR, "token.json")

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# -----------------------------
# Gmail Service
# -----------------------------
def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the token for future runs
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

# -----------------------------
# Check Confirmations
# -----------------------------
def check_confirmations():
    service = get_gmail_service()

    # Search for LinkedIn confirmation emails from last 7 days
    results = service.users().messages().list(
        userId='me',
        q='from:(jobs-noreply@linkedin.com) subject:(Haider Ali, your application was sent to ) newer_than:7d'
    ).execute()

    messages = results.get('messages', [])
    print(f"📬 Found {len(messages)} confirmation emails in the last 7 days.")

    if not messages:
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        snippet = msg_data.get('snippet', '')
        job_link = re.search(r'https://www\.linkedin\.com/jobs/view/\d+', snippet)

        if job_link:
            job_url = job_link.group(0)
            cursor.execute("""
                UPDATE applications
                SET application_status='Confirmed', email_id=?
                WHERE job_url LIKE ? AND application_status='Pending'
            """, (msg['id'], f"%{job_url}%"))
            if cursor.rowcount:
                print(f"✅ Updated status for {job_url}")

    conn.commit()
    conn.close()
    print("✨ Confirmation sync complete!")

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    check_confirmations()
