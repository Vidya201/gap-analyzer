# run.py - start both servers with one command

import subprocess
import sys
import os

def run():
    python = sys.executable

    fastapi_process = subprocess.Popen(
        [python, "-m", "uvicorn", "app:app", "--reload", "--port", "8000"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )

    streamlit_process = subprocess.Popen(
        [python, "-m", "streamlit", "run", "ui.py", "--server.port", "8501"],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )

    print("\n✅ Skill Gap Analyzer is running!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 FastAPI backend  →  http://localhost:8000")
    print("📖 API docs         →  http://localhost:8000/docs")
    print("🎯 Streamlit UI     →  http://localhost:8501")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("\nPress Ctrl+C to stop\n")

    try:
        fastapi_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        fastapi_process.terminate()
        streamlit_process.terminate()

if __name__ == "__main__":
    run()
