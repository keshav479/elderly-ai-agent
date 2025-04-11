import schedule
import time
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ollama import Client
from datetime import datetime

# Initialize Ollama client
ollama_client = Client(host='http://localhost:11434')

# Email configuration
EMAIL_SENDER = "youremail@gmail.com"
EMAIL_PASSWORD = "your_app_password"  # Use App Password
EMAIL_RECEIVER = "recipientemail@gmail.com"

# Function to send email reminder
def send_email_reminder(task, time):
    subject = "🔔 Reminder from your Elderly AI Assistant"
    body = f"Hi there! Just a gentle reminder: '{task}' is scheduled for {time}."

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("✅ Reminder email sent successfully!")
    except Exception as e:
        print("❌ Failed to send email:", e)

# Generate dynamic reminder with LLM
def send_reminder(reminder_text):
    prompt = (
        f"You're a friendly virtual assistant for an elderly person. "
        f"Kindly remind them: '{reminder_text}' in a gentle and cheerful tone."
    )

    try:
        response = ollama_client.generate(model='llama3.2:latest', prompt=prompt)
        message = response['response']
        print("🔔 Reminder:", message)
    except Exception as e:
        print("⚠️ Failed to generate message via LLM:", e)
        print("🔔 Reminder (fallback):", reminder_text)

    # Send email reminder after the LLM response
    send_email_reminder(reminder_text, datetime.now().strftime("%H:%M"))

# Load reminders from DB
def load_reminders():
    conn = sqlite3.connect("data/reminders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT task, time FROM reminders")
    reminders = cursor.fetchall()
    conn.close()
    return reminders

# Schedule all reminders
def schedule_reminders():
    reminders = load_reminders()
    for task, reminder_time in reminders:
        print(f"⏰ Scheduling reminder: '{task}' at {reminder_time}")
        schedule.every().day.at(reminder_time).do(send_reminder, reminder_text=task)

# Main loop
def run():
    print("🚀 Reminder Agent is running...")
    schedule_reminders()
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run()
