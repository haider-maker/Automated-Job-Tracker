# flask_api.py
import os
import threading
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import json

from db.db_functions import add_application
from gmail_checker import check_confirmations

app = Flask(__name__)
CORS(app)

# --------------------------------------------------
# Load config.json (absolute DB path)
# --------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # /Automated-Job-Tracker
ROOT_DIR = os.path.dirname(BASE_DIR)                    # /Job_Tracker
CREDS_DIR = os.path.join(ROOT_DIR, "creds")

with open(os.path.join(CREDS_DIR, "config.json"), "r") as f:
    config = json.load(f)

DB_PATH = config["DB_PATH"]
print(f"Using DB: {DB_PATH}")

# --------------------------------------------------
# Gmail Background Thread
# --------------------------------------------------
def gmail_background_worker():
    print("📥 Gmail Auto-Sync Thread Started")

    while True:
        try:
            check_confirmations()
        except Exception as e:
            print("⚠ Gmail checker error:", e)

        time.sleep(300)  # 5 minutes


def start_gmail_thread():
    worker = threading.Thread(
        target=gmail_background_worker,
        daemon=True
    )
    worker.start()
    print("🧵 Gmail thread initialized")

# --------------------------------------------------
# API Endpoint — Add Job
# --------------------------------------------------
@app.route("/add_job", methods=["POST"])
def add_job():
    data = request.get_json()
    print("📩 Received:", data)

    required = ["company", "position", "job_url", "platform"]
    if not all(field in data for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    add_application(
        date_applied=datetime.now().date().isoformat(),
        platform=data["platform"],
        company=data["company"],
        position=data["position"],
        job_url=data["job_url"],
        notes=data.get("notes", ""),
        application_status="Pending",
        db_path=DB_PATH
    )

    print("✔ Job saved")
    return jsonify({"message": "Job added successfully"}), 200

# --------------------------------------------------
# Start Flask
# --------------------------------------------------
if __name__ == "__main__":
    print(f"🚀 Flask API running with DB: {DB_PATH}")

    start_gmail_thread()
    app.run(port=5000)
