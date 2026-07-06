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


if __name__ == "__main__":
    create_database()
    print("Adatbázis létrehozva.")