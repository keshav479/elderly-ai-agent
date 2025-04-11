# agents/health_monitor_agent.py

import time
import random
import json
from datetime import datetime
from ollama import Client
import os

LOG_FILE = "data/health_log.json"
ollama_client = Client(host="http://localhost:11434")

def generate_health_data():
    return {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'heart_rate': random.randint(55, 110),
        'bp_sys': random.randint(90, 160),
        'bp_dia': random.randint(60, 100),
        'glucose': random.randint(70, 180)
    }

def check_abnormalities(data):
    issues = []
    if data['heart_rate'] < 60 or data['heart_rate'] > 100:
        issues.append("abnormal heart rate")
    if data['bp_sys'] > 140 or data['bp_dia'] > 90:
        issues.append("high blood pressure")
    if data['glucose'] > 140:
        issues.append("elevated glucose level")
    return issues

def generate_alert_message(issues):
    prompt = (
        f"You're a helpful and calming assistant. Notify the caregiver that the patient is showing: {', '.join(issues)}."
    )
    try:
        response = ollama_client.generate(model='llama3.2:latest', prompt=prompt)
        return response['response']
    except Exception as e:
        return f"Error generating alert: {e}"

def log_to_file(entry):
    os.makedirs("data", exist_ok=True)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print("❌ Failed to log:", e)

# ✅ Called by orchestrator to run a single check
def check_health():
    data = generate_health_data()
    alerts = check_abnormalities(data)
    
    message = generate_alert_message(alerts) if alerts else "All vitals normal."

    log_entry = {
        **data,
        'alerts': alerts,
        'message': message
    }

    print(f"[{data['timestamp']}] Vitals: HR={data['heart_rate']} | BP={data['bp_sys']}/{data['bp_dia']} | Glucose={data['glucose']}")
    if alerts:
        print("🚨 ALERT:", message)
    else:
        print("✅ All vitals normal.")

    log_to_file(log_entry)

    # Return for orchestrator
    return {
        'status': 'critical' if alerts else 'normal',
        'message': message,
        'data': data,
        'alerts': alerts
    }

# 🔁 Standalone mode (optional testing)
def run_health_monitor():
    print("🩺 Health Monitor Agent is running...\n")
    while True:
        check_health()
        time.sleep(10)

if __name__ == "__main__":
    run_health_monitor()

