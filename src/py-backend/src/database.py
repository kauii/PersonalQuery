import os
from pathlib import Path

from langchain_community.utilities import SQLDatabase

# Resolve path relative to *this* file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APPDATA_PATH = Path(os.getenv("APPDATA", Path.home()))
DB_PATH = APPDATA_PATH / "personal-analytics" / "database.sqlite"
URI = f"sqlite:///{DB_PATH}"

_db_instance = SQLDatabase.from_uri(URI)


def get_db() -> SQLDatabase:
    return _db_instance
