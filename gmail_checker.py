from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import sqlite3
import os
import re
from datetime import datetime
import os, json

# Always resolve relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "config.json"), "r") as f:
    config = json.load(f)

DB_PATH = config.get("DB_PATH", os.path.join(BASE_DIR, "data", "job_tracker.db"))

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(r"C:\Users\Haider Ali Shahid\OneDrive\Desktop\Job_Tracker\Automated-Job-Tracker\credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def check_confirmations():
    service = get_gmail_service()

    # Search for LinkedIn confirmation emails
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

if __name__ == "__main__":
    check_confirmations()
