# flask_api.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from db.db_functions import add_application

app = Flask(__name__)
CORS(app)

# --- Define consistent absolute DB path ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "job_tracker.db")

@app.route("/add_job", methods=["POST"])
def add_job():
    data = request.get_json()
    print("📩 Received data:", data)  # Debug print

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
        db_path=DB_PATH  # 👈 explicit path here
    )

    print(f"✅ Job added successfully to {DB_PATH}")
    return jsonify({"message": "Job added successfully"}), 200


if __name__ == "__main__":
    print(f"🚀 Flask API running with DB: {DB_PATH}")
    app.run(port=5000)
