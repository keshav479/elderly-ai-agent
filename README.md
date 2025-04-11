# 🧓 Elderly AI Assistant

An intelligent, modular, and empathetic AI assistant designed to support the elderly with daily routines, safety monitoring, health tracking, and communication using a multi-agent architecture.

---

## 💡 Features

- 🩺 **Health Monitoring Agent**: Tracks and logs daily health metrics.
- 🛡 **Safety Monitor Agent**: Detects inactivity or emergencies and sends alerts.
- 🗣 **Communication Agent**: Facilitates interaction through natural language.
- 🧠 **LLM-Powered Intelligence**: Uses `ollama3.2:latest` to generate soft and empathetic responses.
- 🗓 **Reminder Agent**: Manages daily reminders for medicine, hydration, and other activities.
- 🔗 **Orchestrator Agent**: Coordinates tasks across agents.
- 📊 **Streamlit UI**: Clean, user-friendly interface for interaction.
- 🗃 **SQLite3 Database**: Lightweight storage for reminders, health logs, and monitoring data.

---

## 🏗 Project Structure

```plaintext
ELDERLY_AI_ASSISTANT/
│
├── agents/                     # Modular agent logic
│   ├── communication_agent.py
│   ├── health_monitor_agent.py
│   ├── orchestrator_agent.py
│   ├── reminder_agent.py
│   └── safety_monitor_agent.py
│
├── data/                       # Persistent data storage
│   ├── daily_reminder.csv
│   ├── health_log.json
│   ├── health_monitoring.csv
│   ├── reminders.db
│   └── safety_monitoring.csv
│
├── ui/                         # Frontend UI
│   └── app.py
│
├── utils/                      # Utility scripts
│   └── init_db.py
│
├── .env                        # Environment variables
├── main.py                     # Entry point
└── README.md                   # You're here!
```
## 📦 Installation
```
git clone https://github.com/YOUR_USERNAME/elderly-ai-assistant.git
cd elderly-ai-assistant
```
## Create and activate a virtual environment
```
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
## Install dependencies
## ⚙️ Environment Variables (.env)
```
Create a .env file in the root directory and add the following:
SENDER_EMAIL=
SENDER_PASSWORD=
```

## 🧠 LLM Setup with Ollama
## This project uses Ollama as the LLM provider.
```
Install Ollama from https://ollama.com
Run the model
ollama run llama3
Make sure ollama3.2:latest is installed and running locally on port 11434.
```

## 📋 Database Initialization
```
Run the following script to create the required database schema:
python utils/init_db.py
```

## 🚀 Running the App
## Launch the Streamlit UI:
```
streamlit run ui/app.py
```
## Then run the Orchestrator agent by:
```
python main.py
```