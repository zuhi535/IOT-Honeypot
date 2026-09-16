# IoT MQTT Honeypot

A lightweight **MQTT honeypot** that sits behind an [Eclipse Mosquitto](https://mosquitto.org/) broker, silently subscribes to **every topic**, and logs all incoming traffic to a SQLite database — automatically flagging messages that look like brute‑force or default‑credential attack attempts. A dark‑themed **Flask web dashboard** visualizes the captured traffic in real time.

> **Status:** Educational / research honeypot. Not intended to be exposed directly on the public internet without additional hardening (see [Security Notes](#-security-notes)).

---

## 📑 Table of Contents

- [Overview](#overview)
- [Features](#-features)
- [How It Works](#-how-it-works)
- [Project Structure](#-project-structure)
- [Requirements](#-requirements)
- [Getting Started](#-getting-started)
- [Configuration](#-configuration)
- [Database Schema](#-database-schema)
- [Dashboard](#-dashboard)
- [Known Limitation: the `client_id` Field](#-known-limitation-the-client_id-field)
- [Security Notes](#-security-notes)

---

## Overview

IoT devices frequently communicate over **MQTT**, a lightweight publish/subscribe protocol, and are a common target for attackers looking for default credentials, exposed brokers, or misconfigured topics. This project deploys a **decoy MQTT broker** (via Docker) together with a Python client that:

1. Connects to the broker and subscribes to **all topics** (`#`).
2. **Logs every single message** it receives to a local SQLite database.
3. Applies a simple **keyword-based detection** to flag suspicious payloads (e.g. attempts containing `admin`, `root`, `password`, `123456`, …).
4. Exposes a **live dashboard** so you can watch the captured traffic, charts, and flagged events without touching the database directly.

---

## ✨ Features

- 🌐 **Full topic coverage** — subscribes to `#`, so *any* MQTT traffic sent to the broker is captured, regardless of topic name.
- 🚨 **Automatic suspicious-message detection** — if a topic or payload contains one of the configurable keywords in `honeypot/config.py` (`SUSPICIOUS_KEYWORDS`), the entry is stored with `is_suspicious = 1` and logged at `WARNING` level.
- 🧾 **Centralized logging** — a proper `logging`-based setup (`honeypot/logger.py`) replaces ad-hoc `print()` calls; every event is written **simultaneously** to the console and to `logs/honeypot.log`.
- 🗃️ **Rich per-message metadata** stored for every captured event:

  | Field | Description |
  |---|---|
  | `timestamp` | Time the message was received |
  | `topic` | The MQTT topic the message was published to |
  | `payload` | Raw message body |
  | `client_id` | Sender-provided device/client identifier, extracted from JSON payloads when available (see [limitation](#-known-limitation-the-client_id-field) below) |
  | `payload_size` | Message size in bytes |
  | `is_suspicious` | `0`/`1` flag set by the keyword detector |

- 🔄 **Automatic schema migration** — if you already have an older `honeypot.db` with fewer columns, `database.py` (`_migrate_schema`) adds the missing columns on startup **without losing existing data**.
- 📊 **Live analytics dashboard** (Flask + Matplotlib) — bar chart of top topics, pie chart of topic distribution, and a time-series line chart of daily event volume, all rendered server-side as PNGs with a dark theme matching the UI.
- ⚡ **No page reloads** — the dashboard polls `/api/data` every 5 seconds and patches only the parts of the DOM that changed (stats, table rows, chart images), avoiding flicker.
- 🐳 **One-command broker setup** via `docker-compose` (official `eclipse-mosquitto:2` image).
- 🧪 **Simple CLI utilities** to inspect the database (`view_logs.py`) or sanity-check counts (`test_database.py`) without needing the web dashboard.

---

## 🧠 How It Works

```
                 ┌────────────────────┐
  IoT device /   │  Mosquitto Broker  │
  scanner /      │   (Docker, :1883)  │
  attacker  ───► │  allow_anonymous   │
                 └─────────┬──────────┘
                           │  subscribes to "#"
                           ▼
                 ┌────────────────────┐
                 │  honeypot/          │
                 │  mqtt_server.py     │──► logs/honeypot.log (+ console)
                 │  (paho-mqtt client) │
                 └─────────┬──────────┘
                           │ detection.py → is_suspicious()
                           │ database.py  → save_log()
                           ▼
                 ┌────────────────────┐
                 │  database/          │
                 │  honeypot.db        │
                 │  (SQLite)           │
                 └─────────┬──────────┘
                           │ read-only queries
                           ▼
                 ┌────────────────────┐
                 │  dashboard/         │
                 │  app.py (Flask)     │──► charts.py (Matplotlib PNGs)
                 │  templates/index    │──► auto-refreshing web UI
                 └────────────────────┘
```

Because the honeypot connects as an **ordinary subscriber**, any device — legitimate or malicious — that publishes to the broker will have its message captured, timestamped, sized, and (if it matches a keyword) flagged as suspicious.

---

## 📁 Project Structure

```
IOT-Honeypot-2.0/
├── dashboard/
├── honeypot/
├── mosquitto/
├── logs/
├── docker-compose.yml
├── requirements.txt
└── README.md
```

### `honeypot/`

The core of the project — the actual honeypot logic, independent from the web dashboard.

- **`config.py`** — central configuration: broker host/port, the honeypot's own MQTT client ID, filesystem paths (`BASE_DIR`, `DATABASE_PATH`, `LOG_DIR`, `LOG_FILE`), and the `SUSPICIOUS_KEYWORDS` list used for detection.
- **`mqtt_server.py`** — the honeypot's entry point. Connects to the broker, subscribes to `#`, and on every incoming message: extracts a `client_id`/`device_id` from JSON payloads when present, runs suspicion detection, persists the event, and logs it (`WARNING` for suspicious traffic, `INFO` otherwise).
- **`database.py`** — all SQLite access lives here: table creation, automatic schema migration for older databases, inserting new log rows, and a full set of read helpers used by both the CLI tools and the dashboard (`get_logs`, `get_last_logs`, `count_logs`, `count_today_logs`, `get_top_topic`, `get_topic_counts`, `get_events_over_time`, `get_suspicious_logs`, `count_suspicious_logs`, `get_latest_log`, …).
- **`detection.py`** — the keyword-based suspicious-traffic detector. `is_suspicious()` returns a boolean; `matched_keywords()` returns *which* keywords triggered the match, which is used for richer log messages.
- **`logger.py`** — a single shared `logging` configuration used across the whole project (console + rotating‑free file handler to `logs/honeypot.log`), so every module logs consistently instead of using `print()`.
- **`view_logs.py`** — a small CLI tool that dumps every stored log entry to the terminal and prints a total count of suspicious messages.
- **`test_database.py`** — a quick sanity-check script: prints total/suspicious event counts and the most recent log rows, useful while developing without spinning up the dashboard.

### `dashboard/`

A self-contained Flask application that turns the raw database into a live, visual monitor.

- **`app.py`** — defines the Flask app and its routes:
  - `/` — renders the main dashboard page (`index.html`) with the current stats.
  - `/api/data` — JSON endpoint returning the same data, polled every 5 seconds by the front-end for live updates.
  - `/chart/topics-bar.png`, `/chart/topics-pie.png`, `/chart/events-line.png` — dynamically generated PNG chart endpoints.
- **`charts.py`** — generates all Matplotlib charts (bar, pie, line) server-side as in-memory PNG images, styled with a custom dark palette that matches the dashboard's UI.
- **`templates/index.html`** — the dashboard UI itself: summary stat cards (total events, today's events, top topic), the three charts, a "latest event" panel, and a table of recent events with suspicious rows highlighted in red. Includes the JavaScript responsible for polling `/api/data` and patching the DOM/images without a full page reload.
- **`static/`** — reserved for any additional static assets (currently empty).

### `mosquitto/`

Configuration for the decoy MQTT broker used by `docker-compose.yml`.

- **`config/mosquitto.conf`** — minimal broker configuration: listens on port `1883` and allows **anonymous connections** (`allow_anonymous true`), which is intentional — the broker is meant to look like an unsecured, easy target.
- `data/`, `log/` *(created automatically by Docker at runtime, git-ignored)* — Mosquitto's own persistence and native log directory.

### `logs/`

Output directory for the application's own log file (`honeypot.log`), written by `honeypot/logger.py`. Tracked with a `.gitkeep` placeholder; the actual `*.log` files are git-ignored.

### `database/` *(created at first run)*

Not shipped in the repository, but required at runtime: `honeypot/config.py` points `DATABASE_PATH` to `database/honeypot.db`. **Make sure this folder exists before running the honeypot for the first time** (see [Getting Started](#-getting-started)) — SQLite will not create missing parent directories automatically.

---

## 🧰 Requirements

- **Python 3.11+** (developed against 3.13)
- **Docker** and **Docker Compose** (to run the Mosquitto broker)
- The Python packages listed in [`requirements.txt`](./requirements.txt), most notably:

  | Package | Purpose |
  |---|---|
  | `paho-mqtt` | MQTT client used by the honeypot listener |
  | `Flask` | Web dashboard |
  | `matplotlib` | Server-side chart rendering |
  | `pandas` / `numpy` | Data handling for chart generation |
  | `SQLAlchemy` | (available for future DB abstraction) |

---

## 🚀 Getting Started

```bash
# 1. Clone the repository and switch to this branch
git clone https://github.com/zuhi535/IOT-Honeypot.git
cd IOT-Honeypot
git checkout V2.0

# 2. Create the folders the app expects at runtime
mkdir -p database logs

# 3. Start the decoy MQTT broker
docker compose up -d

# 4. Install Python dependencies (ideally inside a virtualenv)
python -m venv .venv
source .venv/bin/activate      # on Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 5. Create / migrate the SQLite database
python -m honeypot.database

# 6. Start the honeypot listener (keep this running in its own terminal)
python -m honeypot.mqtt_server

# 7. (Optional) Inspect captured events from the command line
python -m honeypot.view_logs

# 8. (Optional) Launch the live web dashboard
python -m dashboard.app
# then open http://localhost:5000 in your browser
```

Once the broker and the listener are running, publish a test message to any topic (e.g. with `mosquitto_pub`) and watch it appear in the terminal, in `logs/honeypot.log`, in `honeypot.db`, and on the dashboard.

```bash
mosquitto_pub -h localhost -p 1883 -t "devices/thermostat/config" -m '{"device_id":"th-01","password":"admin123"}'
```

The message above would be stored **and** flagged as suspicious, since its payload contains the keywords `password` and `admin`.

---

## ⚙️ Configuration

All tunables live in **`honeypot/config.py`**:

| Setting | Default | Description |
|---|---|---|
| `BROKER` | `"localhost"` | Hostname/IP of the MQTT broker to connect to |
| `PORT` | `1883` | Broker port |
| `LISTENER_CLIENT_ID` | `"honeypot-listener"` | MQTT client ID the *honeypot itself* uses when connecting (not the ID of the attacker's client — see below) |
| `DATABASE_PATH` | `database/honeypot.db` | Path to the SQLite database file |
| `LOG_DIR` / `LOG_FILE` | `logs/` / `logs/honeypot.log` | Where application logs are written |
| `SUSPICIOUS_KEYWORDS` | `admin`, `root`, `password`, `passwd`, `toor`, `administrator`, `123456`, `login`, `secret`, `default`, `su `, `shell` | Case-insensitive keyword list used to flag traffic as suspicious |

Broker-side settings (listener port, anonymous access) are configured separately in **`mosquitto/config/mosquitto.conf`**.

---

## 🗄️ Database Schema

Table `logs` (SQLite), automatically created and migrated by `honeypot/database.py`:

| Column | Type | Notes |
|---|---|---|
| `id` | `INTEGER PRIMARY KEY AUTOINCREMENT` | |
| `timestamp` | `TEXT` | Format `YYYY-MM-DD HH:MM:SS` |
| `topic` | `TEXT` | MQTT topic the message was published to |
| `payload` | `TEXT` | Raw message body |
| `client_id` | `TEXT` | `"N/A"` unless recoverable from a JSON payload (see below) |
| `payload_size` | `INTEGER` | Size of the message in bytes |
| `is_suspicious` | `INTEGER` | `0` or `1` |

If you already have an older 4-column `honeypot.db`, simply run `python -m honeypot.database` again — the missing columns will be added automatically with safe defaults, and no existing rows are lost.

---

## 📊 Dashboard

Running `python -m dashboard.app` starts a Flask server (default `http://localhost:5000`) that displays:

- **Summary cards** — total events, events captured today, and the most active topic.
- **Bar chart** — message volume per topic.
- **Pie chart** — proportional topic distribution.
- **Line chart** — event volume over time (per day).
- **Latest event panel** — details of the most recently captured message.
- **Recent events table** — the most recent entries, with suspicious rows visually highlighted.

The page refreshes its data every **5 seconds** via `/api/data` and swaps chart images only after they've fully loaded, so the UI updates smoothly without flicker or a full page reload.

---

## ⚠️ Known Limitation: the `client_id` Field

The **MQTT protocol itself does not forward the identity or IP address of the publishing client** inside the `PUBLISH` packet to subscribers — this is a limitation of the protocol/broker design, **not a bug in this code**. Since the honeypot connects as a plain subscribing client behind the Mosquitto broker, it has **no direct way** to read the real attacker's client ID or IP from the `message` object it receives.

**What this project does instead:**

- If the payload is JSON and contains a `client_id` / `device_id` (or `clientId` / `deviceId`) field — as many IoT devices include in their own payloads — that value is extracted and stored.
- Otherwise, the field defaults to `"N/A"`.

**If you need the real attacker's IP/client identifier**, two directions are suggested for a future iteration:

1. **Correlate with the broker's own logs** — parse Mosquitto's log output (`mosquitto/log`) in parallel and join entries with the honeypot's own logs by timestamp.
2. **Replace the subscriber architecture** — instead of connecting as a subscribing MQTT client, implement the honeypot as its own minimal MQTT broker / raw TCP socket server, which *does* see the IP address of every incoming connection at the transport layer.

---

## 🔒 Security Notes

This project is intentionally permissive so that it behaves like an easy target:

- The Mosquitto broker allows **anonymous connections** (`allow_anonymous true`) and has **no TLS/authentication** configured.
- It is designed for **research, learning, and controlled/lab environments** — do **not** expose port `1883` directly to the public internet without additional network isolation (e.g. an isolated VLAN, a reverse proxy, or a cloud security group limiting inbound access), unless that is a deliberate part of your research setup.
- The dashboard (`dashboard/app.py`) runs Flask's built-in development server and does **not** implement authentication — treat it as a local/internal tool only, or put it behind your own auth layer before exposing it more broadly.
