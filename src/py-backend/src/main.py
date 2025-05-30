import uvicorn
from server_rest import app
import logging
import sys
import os
from dotenv import load_dotenv

base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_path, '.env')

# Load .env from that path
load_dotenv(dotenv_path=env_path)


# Log to absolute path so we never get confused
log_path = os.path.join(os.path.dirname(__file__), "backend.log")

logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Also log unhandled exceptions
def handle_exception(exc_type, exc_value, exc_traceback):
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

logging.info("✅ Backend script started")


if __name__ == "__main__":
    logging.info("🚀 Uvicorn starting...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
