from pathlib import Path

# MQTT Broker beállítások
BROKER = "localhost"
PORT = 1883

# A projekt gyökérkönyvtára
BASE_DIR = Path(__file__).resolve().parent.parent

# Az adatbázis teljes elérési útja
DATABASE_PATH = BASE_DIR / "database" / "honeypot.db"