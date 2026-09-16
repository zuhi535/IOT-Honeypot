import json
from datetime import datetime

import paho.mqtt.client as mqtt

from honeypot.config import BROKER, PORT, LISTENER_CLIENT_ID
from honeypot.database import save_log
from honeypot.detection import is_suspicious, matched_keywords
from honeypot.logger import get_logger

logger = get_logger(__name__)


def extract_client_id(payload: str) -> str:
    """Megprobalja kinyerni a device/kliens azonositot a payloadbol,
    ha az JSON es tartalmaz "client_id" vagy "device_id" mezot.

    FONTOS: az MQTT protokoll a PUBLISH csomagban nem kuldi tovabb a
    kuldo kliens MQTT client ID-jat vagy IP-cimet a feliratkozoknak,
    ezert ezt kozvetlenul nem tudjuk kiolvasni - csak akkor van
    ertelmes eredmeny, ha maga a device belerakja a sajat payloadjaba.
    Lasd README "Ismert korlatok" resz.
    """
    try:
        data = json.loads(payload)
    except (json.JSONDecodeError, TypeError):
        return "N/A"

    if isinstance(data, dict):
        for key in ("client_id", "device_id", "clientId", "deviceId"):
            if key in data:
                return str(data[key])

    return "N/A"


def on_connect(client, userdata, flags, reason_code, properties=None):
    logger.info("Csatlakozva az MQTT brokerhez (reason_code=%s).", reason_code)

    client.subscribe("#")
    logger.info("Feliratkozva minden topicra ('#').")


def on_message(client, userdata, message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    topic = message.topic
    payload = message.payload.decode(errors="ignore")

    payload_size = len(message.payload)
    client_id = extract_client_id(payload)
    suspicious = is_suspicious(topic, payload)

    save_log(
        timestamp,
        topic,
        payload,
        client_id=client_id,
        payload_size=payload_size,
        is_suspicious=suspicious,
    )

    if suspicious:
        reasons = matched_keywords(topic, payload)
        logger.warning(
            "GYANUS uzenet! topic=%s | client_id=%s | meret=%d byte | kulcsszavak=%s | payload=%s",
            topic, client_id, payload_size, reasons, payload,
        )
    else:
        logger.info(
            "Uj MQTT uzenet | topic=%s | client_id=%s | meret=%d byte | payload=%s",
            topic, client_id, payload_size, payload,
        )


def main():
    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=LISTENER_CLIENT_ID,
    )

    client.on_connect = on_connect
    client.on_message = on_message

    logger.info("Csatlakozas a brokerhez (%s:%d)...", BROKER, PORT)
    client.connect(BROKER, PORT)

    client.loop_forever()


if __name__ == "__main__":
    main()
