# main.py

from agents.orchestrator_agent import start_orchestrator
import time

if __name__ == "__main__":
    start_orchestrator()

    # Keep the main thread alive to let the orchestrator thread run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Orchestrator stopped.")