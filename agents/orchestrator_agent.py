# agents/orchestrator_agent.py

from datetime import datetime, timedelta
import threading
import time

# Import agent functionalities
from agents.health_monitor_agent import check_health
from agents.safety_monitor_agent import send_safety_alert
from agents.reminder_agent import load_reminders, send_reminder
from agents.communication_agent import get_friendly_message

# In-memory cache to avoid sending the same reminder repeatedly in a short time
sent_reminders = {}

def orchestrate_health_check():
    health = check_health()
    if health['status'] == 'critical':
        send_safety_alert("Health check reported a critical issue.")

def orchestrate_reminders():
    current_time = datetime.now().strftime("%H:%M")
    reminders = load_reminders()
    
    for task, reminder_time in reminders:
        if reminder_time == current_time:
            # Avoid duplicates within the same minute
            if sent_reminders.get((task, reminder_time)) != current_time:
                send_reminder(task)
                sent_reminders[(task, reminder_time)] = current_time

def orchestrate_chat_response(user_input):
    return get_friendly_message(user_input)

def start_orchestrator():
    print("🧠 Orchestrator Agent is now running...")
    
    def loop():
        while True:
            orchestrate_health_check()
            orchestrate_reminders()
            time.sleep(60)  # Check every minute

    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
