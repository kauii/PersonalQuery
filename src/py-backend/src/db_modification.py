import sqlite3
from datetime import datetime


def parse_datetime_no_ms(dt_str):
    return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")


def update_sessions_from_usage_data(db_path):
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    cur = conn.cursor()

    # Ensure session table exists
    cur.execute('''
        CREATE TABLE IF NOT EXISTS session (
            id TEXT PRIMARY KEY,
            startedAt TEXT,
            endedAt TEXT,
            durationInSeconds INTEGER,
            question TEXT,
            scale INTEGER,
            response TEXT,
            skipped BOOLEAN
        )
    ''')

    # Load usage data (ordered chronologically)
    cur.execute('''
        SELECT id, created_at, type FROM usage_data
        WHERE type IN ('APP_START', 'EXPERIENCE_SAMPLING_AUTOMATICALLY_OPENED', 'APP_QUIT')
        ORDER BY created_at ASC
    ''')
    usage_rows = cur.fetchall()

    # Load responses into a dict (truncated promptedAt -> row)
    cur.execute('''
        SELECT id, promptedAt, question, scale, response, skipped
        FROM experience_sampling_responses
    ''')
    esr_raw = cur.fetchall()
    esr_map = {
        promptedAt.split('.')[0]: (id_, question, scale, response, skipped)
        for (id_, promptedAt, question, scale, response, skipped) in esr_raw
    }

    sessions = []
    current_start = None

    for i, (uid, created_at, typ) in enumerate(usage_rows):
        if typ == 'APP_START':
            current_start = created_at

        elif typ == 'EXPERIENCE_SAMPLING_AUTOMATICALLY_OPENED' and current_start:
            started_dt = parse_datetime_no_ms(current_start)
            ended_dt = parse_datetime_no_ms(created_at)
            duration = int((ended_dt - started_dt).total_seconds())

            esr = esr_map.get(created_at)
            esr_id, question, scale, response, skipped = esr if esr else (None, None, None, None, None)

            if question == "Compared to your normal level of productivity, how productive do you consider the previous session?":
                question = "How productive was this session?"
            elif question == "How well did you spend your time in the previous session?":
                question = "How well spent time?"

            sessions.append((
                uid,  # use usage_data ID as session ID
                current_start,
                created_at,
                duration,
                question,
                scale,
                response,
                skipped
            ))

            current_start = created_at

        elif typ == 'APP_QUIT' and current_start:
            started_dt = parse_datetime_no_ms(current_start)
            ended_dt = parse_datetime_no_ms(created_at)
            duration = int((ended_dt - started_dt).total_seconds())

            sessions.append((
                uid,
                current_start,
                created_at,
                duration,
                None, None, None, None
            ))

            current_start = None  # session ends

    # Load existing session IDs to avoid duplicates
    cur.execute('SELECT id FROM session')
    existing_ids = set(row[0] for row in cur.fetchall())

    for session in sessions:
        if session[0] in existing_ids:
            continue

        cur.execute('''
            INSERT INTO session (
                id, startedAt, endedAt, durationInSeconds,
                question, scale, response, skipped
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', session)

    cur.execute('DELETE FROM session WHERE durationInSeconds IS NOT NULL AND durationInSeconds < 300')
    conn.commit()
    conn.close()


def add_window_activity_durations(db_path):
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    cur = conn.cursor()

    # Try to add column
    try:
        cur.execute('ALTER TABLE window_activity ADD COLUMN durationInSeconds INTEGER')
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Fetch window activations sorted by timestamp
    cur.execute('SELECT rowid, ts FROM window_activity ORDER BY ts ASC')
    rows = cur.fetchall()

    for i in range(len(rows) - 1):
        current_rowid, current_ts = rows[i]
        next_ts = rows[i + 1][1]

        start_dt = datetime.fromisoformat(current_ts)
        end_dt = datetime.fromisoformat(next_ts)
        duration = int((end_dt - start_dt).total_seconds())

        cur.execute('''
            UPDATE window_activity
            SET durationInSeconds = ?
            WHERE rowid = ?
        ''', (duration, current_rowid))

    conn.commit()
    conn.close()
