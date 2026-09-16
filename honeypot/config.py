from pathlib import Path

# MQTT Broker beállítások
BROKER = "localhost"
PORT = 1883

# Ezzel az azonosítóval jelentkezik be a honeypot a brokerre.
# (Nem az üzenetet KÜLDŐ kliens azonosítója - lásd README "Ismert korlátok" rész.)
LISTENER_CLIENT_ID = "honeypot-listener"

# A projekt gyökérkönyvtára
BASE_DIR = Path(__file__).resolve().parent.parent

# Az adatbázis teljes elérési útja
DATABASE_PATH = BASE_DIR / "database" / "honeypot.db"

# Naplófájlok könyvtára és elérési útja (logging modulhoz)
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "honeypot.log"

# Gyanús MQTT üzenetekben keresett kulcsszavak (kis- és nagybetű független)
# Ezek tipikus IoT eszközök elleni brute-force / default credential próbálkozásokra utalnak.
SUSPICIOUS_KEYWORDS = [
    "admin",
    "root",
    "password",
    "passwd",
    "toor",
    "administrator",
    "123456",
    "login",
    "secret",
    "default",
    "su ",
    "shell",
]