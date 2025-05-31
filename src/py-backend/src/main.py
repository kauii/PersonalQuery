import os
import signal
import sys
import logging
from server_rest import app
import uvicorn

appdata_dir = os.getenv("APPDATA", os.getcwd())
log_dir = os.path.join(appdata_dir, "personal-analytics", "logs")
os.makedirs(log_dir, exist_ok=True)

log_path = os.path.join(log_dir, "backend.log")

logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def handle_exception(exc_type, exc_value, exc_traceback):
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


def handle_exit(signum, frame):
    logging.info("🔚 Backend received exit signal")
    sys.exit(0)


signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

if __name__ == "__main__":
    logging.info("🚀 Uvicorn starting...")
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": "%(asctime)s - %(levelname)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "file": {
                    "level": "DEBUG",
                    "class": "logging.FileHandler",
                    "filename": log_path,
                    "formatter": "default",
                },
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                },
            },
            "loggers": {
                "uvicorn": {"handlers": ["file"], "level": "DEBUG"},
                "uvicorn.error": {"handlers": ["file"], "level": "DEBUG"},
                "uvicorn.access": {"handlers": ["file"], "level": "DEBUG"},
            },
        }
    )
