import os
import signal
import sys
import logging
from uvicorn import Config, Server
from server_rest import app

IS_PACKAGED = hasattr(sys, "_MEIPASS")

if IS_PACKAGED:
    appdata_dir = os.getenv("APPDATA", os.getcwd())
    log_dir = os.path.join(appdata_dir, "personal-analytics", "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, "backend.log")
else:
    log_path = None

log_handlers = ["default"]
if log_path:
    log_handlers.append("file")

logging_config = {
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
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": log_path if log_path else "backend.log",
            "formatter": "default",
        },
    },
    "loggers": {
        "uvicorn": {"handlers": log_handlers, "level": "INFO"},
        "uvicorn.error": {"handlers": log_handlers, "level": "INFO"},
        "uvicorn.access": {"handlers": log_handlers, "level": "INFO"},
    },
}


def handle_exception(exc_type, exc_value, exc_traceback):
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))


sys.excepthook = handle_exception


def handle_exit(signum, frame):
    logging.info("Backend received exit signal")
    sys.exit(0)


signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

if __name__ == "__main__":
    logging.info("Uvicorn starting...")

    config = Config(
        app=app,
        host="127.0.0.1",
        port=8000,
        loop="asyncio",
        lifespan="on",
        log_config=logging_config,
    )

    server = Server(config)
    server.run()
