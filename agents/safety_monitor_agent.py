# agents/safety_monitor_agent.py

import time
import random
from datetime import datetime, timedelta
from ollama import Client

# Optional: Connect to your LLM for empathetic alerts
ollama_client = Client(host='http://localhost:11434')

# In-memory activity log
last_movement_time = datetime.now()

# Send a safety alert (with optional LLM tone)
def send_safety_alert(reason):
    prompt = f"You are a gentle assistant. Raise an alert because: {reason}. Keep the tone soft and reassuring."
    try:
        response = ollama_client.generate(model='llama3.2:latest', prompt=prompt)
        message = response['response']
        print("🚨 Safety Alert:", message)
        return message
    except Exception as e:
        print("⚠️ LLM fallback:", e)
        fallback = f"🚨 Alert: {reason}. Please check on the individual."
        print(fallback)
        return fallback

# Simulate movement detection
def detect_movement():
    # 80% chance of movement
    return random.random() < 0.8

# Run safety monitoring loop
def run_safety_monitor():
    global last_movement_time
    print("🛡️ Safety Monitor Agent is running...")

    while True:
        movement = detect_movement()
        current_time = datetime.now()

        if movement:
            last_movement_time = current_time
            print(f"✅ Movement detected at {current_time.strftime('%H:%M:%S')}")
        else:
            # Check if inactive for more than 2 minutes
            if current_time - last_movement_time > timedelta(minutes=2):
                reason = "No movement detected for over 2 minutes"
                send_safety_alert(reason)
                # Reset so it doesn't spam
                last_movement_time = current_time

        time.sleep(10)  # Simulate data every 10 seconds

if __name__ == "__main__":
    run_safety_monitor()
