"""MQTT pub/sub smoke test."""
from __future__ import annotations

import time
from threading import Event

from smart_messaging_core import MqttClient, MqttConfig


def main() -> None:
    topic = "smart-messaging-core/demo"
    received = Event()

    def on_message(payload: dict) -> None:
        print(f"MQTT received payload: {payload}")
        received.set()

    client = MqttClient(MqttConfig(host="192.168.1.60", port=1883, qos=1, retain=False))

    try:
        client.subscribe(topic, on_message)
        time.sleep(0.5)
        ok = client.publish(topic, {"message": "hello mqtt"})
        print(f"MQTT publish returned: {ok}")
        print(f"MQTT subscribe received: {received.wait(timeout=5)}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
