# run.py - start both servers with one command, waiting for the backend to be
# actually ready before starting the frontend (the original started them at the
# same time, so the UI's first request could race the backend booting up).

import subprocess
import sys
import os
import time
import requests

HEALTH_URL = "http://localhost:8000/health"
STARTUP_TIMEOUT = 30  # seconds


def wait_for_backend(timeout=STARTUP_TIMEOUT):
    start = time.time()
    while time.time() - start < timeout:
        try:
            if requests.get(HEALTH_URL, timeout=1).status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(0.5)
    return False


def run():
    python = sys.executable
    cwd = os.path.dirname(os.path.abspath(__file__))

    fastapi_process = subprocess.Popen(
        [python, "-m", "uvicorn", "app:app", "--reload", "--port", "8000"],
        cwd=cwd,
    )

    print("⏳ Waiting for FastAPI backend to start...")
    if not wait_for_backend():
        print("❌ Backend didn't start within 30s. Check the logs above for errors "
              "(e.g. a missing GROQ_API_KEY in your .env file).")
        fastapi_process.terminate()
        return

    streamlit_process = subprocess.Popen(
        [python, "-m", "streamlit", "run", "ui.py", "--server.port", "8501"],
        cwd=cwd,
    )

    print("\n✅ Skill Gap Analyzer is running!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 FastAPI backend  →  http://localhost:8000")
    print("📖 API docs         →  http://localhost:8000/docs")
    print("🎯 Streamlit UI     →  http://localhost:8501")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("\nPress Ctrl+C to stop\n")

    try:
        while True:
            time.sleep(1)
            # if either process dies on its own, stop the other and exit
            if fastapi_process.poll() is not None or streamlit_process.poll() is not None:
                break
    except KeyboardInterrupt:
        pass
    finally:
        print("\nShutting down...")
        fastapi_process.terminate()
        streamlit_process.terminate()


if __name__ == "__main__":
    run()
