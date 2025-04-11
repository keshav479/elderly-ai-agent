# agents/communication_agent.py

from ollama import Client

# Initialize Ollama client
ollama_client = Client(host='http://localhost:11434')

def get_friendly_message(user_input: str):
    prompt = (
        "You're a warm, friendly assistant designed to support elderly users. "
        f"Respond kindly and cheerfully to: '{user_input}'"
    )
    
    try:
        response = ollama_client.generate(model='llama3.2:latest', prompt=prompt)
        return response['response'].strip()
    except Exception as e:
        return f"Sorry, I had trouble responding just now: {e}"
