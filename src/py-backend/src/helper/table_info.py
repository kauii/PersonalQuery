import os
import sqlite3
from pathlib import Path

from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APPDATA_PATH = Path(os.getenv("APPDATA", Path.home()))
DB_PATH = APPDATA_PATH / "personal-analytics" / "database_cut_columns.sqlite"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)

readonly_connection = sqlite3.connect(
    f"file:{DB_PATH}?mode=ro",
    uri=True,
    check_same_thread=False
)

engine = create_engine(
    "sqlite://",
    creator=lambda: readonly_connection,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)

_db_instance = SQLDatabase(engine)


def get_db_copy() -> SQLDatabase:
    return _db_instance
