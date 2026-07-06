import sqlite3

from honeypot.config import DATABASE_PATH


def create_database():
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            topic TEXT,
            payload TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_log(timestamp, topic, payload):
    conn = sqlite3.connect(str(DATABASE_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO logs(timestamp, topic, payload)
        VALUES (?, ?, ?)
    """, (timestamp, topic, payload))

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


if __name__ == "__main__":
    create_database()
    print("Adatbázis létrehozva.")