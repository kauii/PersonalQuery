import sqlite3
import shutil

from dotenv import load_dotenv
from langchain import hub
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate

from database import APPDATA_PATH

DB_PATH = APPDATA_PATH / "personal-analytics" / "database.sqlite"
BACKUP_PATH = APPDATA_PATH / "personal-analytics" / "database_cut_columns.sqlite"


def copy_db_and_trim_columns():
    # Step 1: Copy the database
    BACKUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DB_PATH, BACKUP_PATH)
    print(f"Database copied to {BACKUP_PATH}")

    # Step 2: Connect to the copied database
    conn = sqlite3.connect(str(BACKUP_PATH))
    cur = conn.cursor()

    # Step 3: Cut columns from `window_activity`
    cur.executescript("""
        CREATE TABLE window_activity_new (
            id TEXT PRIMARY KEY,
            windowTitle TEXT,
            processName TEXT,
            activity TEXT,
            ts TEXT,
            durationInSeconds REAL
        );

        INSERT INTO window_activity_new (id, windowTitle, processName, activity, ts, durationInSeconds)
        SELECT id, windowTitle, processName, activity, ts, durationInSeconds
        FROM window_activity;

        DROP TABLE window_activity;
        ALTER TABLE window_activity_new RENAME TO window_activity;
    """)
    print("Trimmed columns in 'window_activity'")

    # Step 4: Cut columns from `user_input`
    cur.executescript("""
        CREATE TABLE user_input_new (
            id TEXT PRIMARY KEY,
            keysTotal INTEGER,
            clickTotal INTEGER,
            movedDistance REAL,
            scrollDelta REAL,
            tsStart TEXT,
            tsEnd TEXT
        );

        INSERT INTO user_input_new (id, keysTotal, clickTotal, movedDistance, scrollDelta, tsStart, tsEnd)
        SELECT id, keysTotal, clickTotal, movedDistance, scrollDelta, tsStart, tsEnd
        FROM user_input;

        DROP TABLE user_input;
        ALTER TABLE user_input_new RENAME TO user_input;
    """)
    print("Trimmed columns in 'user_input'")

    conn.commit()
    conn.close()
    print("Column trimming completed.")


#db = SQLDatabase.from_uri(f"sqlite:///{BACKUP_PATH}")
#print(db.get_table_info())


load_dotenv()
ui_template: ChatPromptTemplate = hub.pull("user_input")
print(type(ui_template.messages[0].prompt.template))
