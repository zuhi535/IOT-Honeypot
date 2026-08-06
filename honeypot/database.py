import sqlite3

from honeypot.config import DATABASE_PATH
from honeypot.logger import get_logger

logger = get_logger(__name__)

# Ha egy régebbi honeypot.db-t nyitunk meg, ezekkel az oszlopokkal egészítjük ki.
# (oszlopnév, SQL típus, alapérték a régi sorokhoz)
_NEW_COLUMNS = [
    ("client_id", "TEXT", "'N/A'"),
    ("payload_size", "INTEGER", "0"),
    ("is_suspicious", "INTEGER", "0"),
]


def create_database():
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            topic TEXT,
            payload TEXT,
            client_id TEXT,
            payload_size INTEGER,
            is_suspicious INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()

    _migrate_schema()


def _migrate_schema():
    """Régebbi (4 oszlopos) honeypot.db fájlokhoz hozzáadja az új oszlopokat,
    hogy a meglévő adatbázis ne törjön el az új funkciók bevezetésekor."""
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(logs)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    for column_name, column_type, default_value in _NEW_COLUMNS:
        if column_name not in existing_columns:
            cursor.execute(
                f"ALTER TABLE logs ADD COLUMN {column_name} {column_type} DEFAULT {default_value}"
            )
            logger.info("Adatbázis migrálva: '%s' oszlop hozzáadva.", column_name)

    conn.commit()
    conn.close()


def save_log(timestamp, topic, payload, client_id="N/A", payload_size=None, is_suspicious=False):
    if payload_size is None:
        payload_size = len(payload.encode("utf-8"))

    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO logs(timestamp, topic, payload, client_id, payload_size, is_suspicious)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (timestamp, topic, payload, client_id, payload_size, int(is_suspicious)))

    conn.commit()
    conn.close()


def get_logs():
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM logs")

    logs = cursor.fetchall()

    conn.close()

    return logs


def count_logs():
    conn = sqlite3.connect(str(DATABASE_PATH))

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM logs")

    total = cursor.fetchone()[0]

    conn.close()

    return total


def get_last_logs(limit=20):

    conn = sqlite3.connect(str(DATABASE_PATH))

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM logs
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    logs = cursor.fetchall()

    conn.close()

    return logs


def get_top_topic():
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT topic, COUNT(*)
        FROM logs
        GROUP BY topic
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """)

    result = cursor.fetchone()

    conn.close()

    return result


def count_today_logs():
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM logs
        WHERE DATE(timestamp) = DATE('now')
    """)

    total = cursor.fetchone()[0]

    conn.close()

    return total


def get_latest_log():

    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM logs
        ORDER BY id DESC
        LIMIT 1
    """)

    log = cursor.fetchone()

    conn.close()

    return log


def get_topic_counts():
    """Minden topic és hozzá tartozó üzenetszám, csökkenő sorrendben.
    Ez adja az adatot az oszlop- és kördiagramhoz."""

    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT topic, COUNT(*) AS db_count
        FROM logs
        GROUP BY topic
        ORDER BY db_count DESC
    """)

    result = cursor.fetchall()

    conn.close()

    return result


def get_events_over_time():
    """Napi bontásban megszámolja az eseményeket.
    Ez adja az adatot a vonaldiagramhoz."""

    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DATE(timestamp) AS day, COUNT(*) AS db_count
        FROM logs
        GROUP BY day
        ORDER BY day ASC
    """)

    result = cursor.fetchall()

    conn.close()

    return result


def get_suspicious_logs(limit=20):
    """A legutóbbi gyanúsnak jelölt üzenetek."""
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM logs
        WHERE is_suspicious = 1
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    logs = cursor.fetchall()

    conn.close()

    return logs


def count_suspicious_logs():
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM logs WHERE is_suspicious = 1")

    total = cursor.fetchone()[0]

    conn.close()

    return total


if __name__ == "__main__":
    create_database()
    print("Adatbázis létrehozva (és migrálva, ha szükséges volt).")