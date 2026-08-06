# IoT MQTT Honeypot

Egyszerű MQTT honeypot, ami egy [Eclipse Mosquitto](https://mosquitto.org/) brokerre feliratkozva
minden bejövő üzenetet naplóz egy SQLite adatbázisba, és automatikusan megjelöli a gyanús
(pl. brute-force / default credential) próbálkozásokat.

## Funkciók

- **Minden topicra feliratkozik** (`#`), így bármilyen MQTT forgalmat rögzít.
- **Gyanús üzenetek automatikus felismerése**: ha a topic vagy a payload olyan kulcsszavakat
  tartalmaz, mint `admin`, `root`, `password`, `123456` stb. (lásd `honeypot/config.py` ->
  `SUSPICIOUS_KEYWORDS`), az üzenet `is_suspicious=1` jelölést kap, és `WARNING` szinten kerül
  naplózásra.
- **`logging` modul** a `print()` helyett: minden esemény egyszerre kerül kiírásra a konzolra
  és a `logs/honeypot.log` fájlba (`honeypot/logger.py`).
- **Részletesebb naplózás** minden üzenetről:
  - `timestamp` – időbélyeg
  - `topic` – MQTT topic
  - `payload` – az üzenet törzse
  - `client_id` – a küldő eszköz azonosítója, ha a payload JSON és tartalmazza (lásd lentebb)
  - `payload_size` – az üzenet mérete byte-ban
  - `is_suspicious` – 0/1, gyanúsnak minősült-e az üzenet

A meglévő `honeypot.db` fájl automatikusan migrálódik az új oszlopokkal, a régi bejegyzések
nem vesznek el (`database.py` -> `_migrate_schema`).

## Ismert korlát: a `client_id` mező

Az MQTT protokoll a `PUBLISH` csomagban **nem küldi tovább** az üzenetet küldő kliens
azonosítóját vagy IP-címét a feliratkozóknak – ez a broker és a kliensek közötti protokoll
tervezéséből adódik, nem a kód hibája. Mivel ez a honeypot egy sima feliratkozó kliensként
működik a mosquitto broker mögött, a *tényleges* támadó azonosítóját közvetlenül nem tudjuk
kiolvasni a `message` objektumból.

Amit ehelyett teszünk:
- Ha a payload JSON, és tartalmaz `client_id` / `device_id` mezőt (sok IoT eszköz így küldi
  a saját azonosítóját), azt kiolvassuk és eltároljuk.
- Ha nem, a mező értéke `"N/A"` lesz.

Ha a projekt következő lépéseként valódi támadói IP-cím/kliens-azonosító kellene, két irány van:
1. A mosquitto broker saját log fájljának (`mosquitto/log`) párhuzamos feldolgozása és
   időbélyeg alapú összekötése a honeypot naplóival.
2. A honeypot átalakítása: ne feliratkozó kliensként, hanem saját minimál MQTT broker/socket
   szerverként fusson, ami TCP szinten látja a bejövő kapcsolatok IP-címét.

## Futtatás

```bash
docker compose up -d          # mosquitto broker indítása
pip install -r requirements.txt
python -m honeypot.database    # adatbázis létrehozása / migrálása
python -m honeypot.mqtt_server # honeypot indítása
python -m honeypot.view_logs   # naplók megtekintése
```
