import os
from langchain_community.utilities import SQLDatabase

# Resolve path relative to *this* file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "../db/database.sqlite")  # this assumes the .sqlite file is in /db/
URI = f"sqlite:///{DB_PATH}"

_db_instance = SQLDatabase.from_uri(URI)


def get_db() -> SQLDatabase:
    return _db_instance
