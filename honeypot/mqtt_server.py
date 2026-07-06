import paho.mqtt.client as mqtt

print("MQTT_SERVER.PY BETÖLTVE!")

from datetime import datetime

from honeypot.config import BROKER, PORT
from honeypot.database import save_log

def on_connect(client, userdata, flags, reason_code, properties=None):
    print("Csatlakozva az MQTT Brokerhez!")

    # Feliratkozás minden topicra
    client.subscribe("#")

    print("Feliratkozás minden topicra.")


def on_message(client, userdata, message):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    topic = message.topic

    payload = message.payload.decode(errors="ignore")

    print("\n=== Új MQTT üzenet ===")
    print(f"Idő: {timestamp}")
    print(f"Topic: {topic}")
    print(f"Payload: {payload}")

    save_log(
        timestamp,
        topic,
        payload
    )

    print("✔ Napló elmentve az adatbázisba.")


client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT)

print("Brokerhez csatlakozás...")

client.loop_forever()