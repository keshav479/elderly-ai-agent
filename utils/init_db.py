# utils/init_db.py
import sqlite3
import os

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)

# Connect to (or create) the database
conn = sqlite3.connect("data/reminders.db")
cursor = conn.cursor()

# Create the reminders table
cursor.execute("""
CREATE TABLE IF NOT EXISTS reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    time TEXT NOT NULL
)
""")

# Optional: Add a sample reminder
cursor.execute("INSERT INTO reminders (task, time) VALUES (?, ?)", 
               ("Take your 10 AM medicine", "10:00"))

conn.commit()
conn.close()

print("✅ Database initialized successfully.")
