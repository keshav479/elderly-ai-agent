import time
import random
import threading
from datetime import datetime, timedelta
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import streamlit as st
from ollama import Client
import json
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.communication_agent import get_friendly_message
from dotenv import load_dotenv
load_dotenv()


# --- Database Setup ---
DB_PATH = "data/reminders.db"

def init_db():
    if not os.path.exists("data"):
        os.makedirs("data")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            time TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()


# --- Email Sending Function ---
def send_email(subject, body, recipient_email):
    sender_email = os.getenv("SENDER_EMAIL")  # set your email as an environment variable
    sender_password = os.getenv("SENDER_PASSWORD")  # set your email password as an environment variable

    if not sender_email or not sender_password:
        print("Please set the sender email and password in environment variables.")
        return

    try:
        # Set up the MIME
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Use TLS encryption
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
            print(f"Email sent successfully to {recipient_email}")

    except smtplib.SMTPAuthenticationError as e:
        print(f"Failed to authenticate: {e}")
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


# --- Streamlit UI Setup ---
st.set_page_config(page_title="Elderly AI Assistant", layout="centered")
st.title("🤖 Elderly AI Assistant Dashboard")

tabs = st.tabs(["💊 Reminders", "🩺 Health Monitor", "🛡️ Safety Monitor", "💬 Communication"])


# --- DB Helper Functions ---
def get_reminders():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, task, time FROM reminders ORDER BY time")
    rows = cursor.fetchall()
    conn.close()
    return rows

def add_reminder(task, time):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reminders (task, time) VALUES (?, ?)", (task, time))
    conn.commit()
    conn.close()

def delete_reminder(reminder_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()


# --- Reminders Tab ---
with tabs[0]:
    st.subheader("📅 Daily Reminders")

    # Get current time in 24-hour format
    now = datetime.now().strftime("%H:%M")

    # Check for reminders and send email if time matches
    reminders = get_reminders()
    for rid, task, time_val in reminders:
        # Check if reminder time matches current time
        if time_val == now:
            st.toast(f"🔔 Reminder: {task}", icon="⏰")

            # Send email notification
            recipient_email = "recipient_email@example.com"  # replace with recipient's email
            subject = "Reminder Notification"
            body = f"Your reminder: {task} is scheduled for {time_val}. Please take the necessary action."
            send_email(subject, body, recipient_email)

    # Display existing reminders
    if reminders:
        for rid, task, time_val in reminders:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"**🕒 {time_val}** — {task}")
            with col2:
                if st.button("❌", key=f"delete_{rid}"):
                    delete_reminder(rid)
                    st.success(f"Deleted reminder '{task}'")
                    st.rerun()
    else:
        st.info("No reminders scheduled yet.")

    st.divider()

    # Add new reminder form
    st.subheader("➕ Add New Reminder")
    with st.form("add_reminder_form"):
        new_task = st.text_input("Reminder Text", placeholder="Take your 9 AM medicine")
        new_time = st.time_input("Time")
        submitted = st.form_submit_button("Add Reminder")

        if submitted:
            if new_task.strip():
                formatted_time = new_time.strftime("%H:%M")  # Time in 24-hour format
                add_reminder(new_task.strip(), formatted_time)
                st.success(f"Added reminder: '{new_task.strip()}' at {formatted_time}")
                st.rerun()
            else:
                st.warning("Please enter a reminder task.")

    st.divider()

    # Load historical reminders from CSV
    st.subheader("🗃️ Historical Reminders")
    with st.expander("📂 Show Reminder Logs"):
        try:
            reminder_df = pd.read_csv("data/daily_reminder.csv")

            reminder_df['datetime'] = pd.to_datetime(reminder_df['Timestamp'], errors='coerce')
            reminder_df['scheduled_hour'] = pd.to_datetime(reminder_df['Scheduled Time'], format="%H:%M:%S", errors='coerce').dt.time

            st.write("### Recent Reminders")
            st.dataframe(reminder_df[['Device-ID/User-ID', 'datetime', 'Reminder Type', 'scheduled_hour', 'Reminder Sent (Yes/No)', 'Acknowledged (Yes/No)']].tail(100))

        except Exception as e:
            st.error(f"❌ Failed to load daily_reminder.csv: {e}")





# --- Health Monitor Tab ---
with tabs[1]:
    st.subheader("🩺 Health Monitoring")

    log_file = "data/health_log.json"
    if not os.path.exists(log_file):
        st.info("No health data available yet. Start the health monitor agent.")
    else:
        with open(log_file, "r") as f:
            entries = [json.loads(line) for line in f.readlines()][-10:]

        for entry in reversed(entries):
            st.markdown(f"**🕒 {entry['timestamp']}**")
            st.markdown(f"- Heart Rate: `{entry['heart_rate']} bpm`")
            st.markdown(f"- Blood Pressure: `{entry['bp_sys']}/{entry['bp_dia']}` mmHg")
            st.markdown(f"- Glucose Level: `{entry['glucose']} mg/dL`")
            if entry['alerts']:
                st.error(f"🚨 Alerts: {', '.join(entry['alerts'])}")
                st.info(f"💬 Assistant says: {entry['message']}")
            else:
                st.success("✅ All vitals normal.")
            st.divider()



# --- Safety Monitor Tab ---
with tabs[2]:
    st.subheader("🛡️ Safety Monitoring")
    st.info("This section handles fall detection, inactivity alerts, and caregiver notifications.")

    # Load historical safety data
    try:
        safety_df = pd.read_csv("data/safety_monitoring.csv", parse_dates=["Timestamp"])
        safety_df["Timestamp"] = pd.to_datetime(safety_df["Timestamp"])
        st.markdown("#### 📊 Historical Safety Records")
        st.dataframe(safety_df.tail(10), use_container_width=True)

        fall_counts = safety_df["Fall Detected (Yes/No)"].value_counts()
        st.markdown("#### 🚨 Fall Detection Summary")
        st.bar_chart(fall_counts)

        location_counts = safety_df["Location"].value_counts()
        st.markdown("#### 🏠 Incident Locations")
        st.bar_chart(location_counts)

    except Exception as e:
        st.warning(f"Could not load safety_monitoring.csv: {e}")

    # Live monitoring setup
    ollama_client = Client(host='http://localhost:11434')

    if 'safety_log' not in st.session_state:
        st.session_state.safety_log = []
    if 'last_movement_time' not in st.session_state:
        st.session_state.last_movement_time = datetime.now()
    if 'movement_history' not in st.session_state:
        st.session_state.movement_history = []

    def detect_movement():
        return random.random() < 0.85  # 85% chance of movement

    def send_safety_alert(reason):
        prompt = (
            f"You are a caring assistant. Kindly alert the caregiver: '{reason}'. "
            f"Make sure your message is polite, calm, and helpful."
        )
        try:
            response = ollama_client.generate(model='llama3.2:latest', prompt=prompt)
            message = response['response']
            timestamp = datetime.now().strftime('%H:%M:%S')
            st.session_state.safety_log.append(f"🚨 {timestamp} - {message}")
        except Exception as e:
            st.session_state.safety_log.append(f"⚠️ Failed to generate alert: {e}")

    def run_safety_monitor():
        while True:
            time.sleep(10)
            movement = detect_movement()
            now = datetime.now()

            if movement:
                st.session_state.last_movement_time = now
                st.session_state.safety_log.append(f"✅ {now.strftime('%H:%M:%S')} - Movement detected.")
                st.session_state.movement_history.append((now, 1))
            else:
                st.session_state.movement_history.append((now, 0))
                inactive_time = now - st.session_state.last_movement_time
                if inactive_time > timedelta(minutes=2):
                    send_safety_alert("No movement detected for over 2 minutes")
                    st.session_state.last_movement_time = now

    if 'safety_thread_started' not in st.session_state:
        import threading
        thread = threading.Thread(target=run_safety_monitor, daemon=True)
        thread.start()
        st.session_state.safety_thread_started = True

    # Live status UI
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Last Movement", st.session_state.last_movement_time.strftime('%H:%M:%S'))
    with col2:
        time_diff = datetime.now() - st.session_state.last_movement_time
        if time_diff < timedelta(minutes=2):
            col2.success("✅ Active - Movement Detected")
        else:
            col2.error("🔴 Inactive - No Recent Movement")

    # Real-time chart
    if st.session_state.movement_history:
        timestamps, values = zip(*st.session_state.movement_history[-30:])
        df = pd.DataFrame({"Time": timestamps, "Movement": values})
        df["Time"] = df["Time"].dt.strftime('%H:%M:%S')
        st.line_chart(df.set_index("Time"))

    if st.button("Trigger Manual Alert"):
        send_safety_alert("Manual safety alert triggered by user")

    with st.expander("🔍 Activity Log (Click to Expand)", expanded=False):
        for log in reversed(st.session_state.safety_log[-50:]):
            st.write(log)







# --- Communication Tab ---
with tabs[3]:
    st.subheader("💬 Communication Assistant")
    st.markdown("Ask me anything or just say hi!")

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if not st.session_state.messages:
        welcome = "👵 Hello dear! I'm here to chat with you anytime you like. 😊"
        st.session_state.messages.append({"role": "assistant", "content": welcome})

    for msg in st.session_state.messages:
        avatar = "🧓" if msg["role"] == "user" else "👨🏻‍⚕️"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    user_input = st.chat_input("Type your message here...")
    if user_input:
        with st.chat_message("user", avatar="🧓"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("assistant", avatar="👨🏻‍⚕️"):
            with st.spinner("Thinking..."):
                reply = get_friendly_message(user_input)
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
