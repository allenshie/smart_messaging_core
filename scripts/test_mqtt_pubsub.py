"""MQTT pub/sub smoke test."""
from __future__ import annotations

import os
import time
from threading import Event

from smart_messaging_core import MqttClient, MqttConfig


def main() -> None:
    topic = os.getenv("SMC_MQTT_TOPIC", "smart-messaging-core/demo")
    host = os.getenv("SMC_MQTT_HOST", "127.0.0.1")
    port = int(os.getenv("SMC_MQTT_PORT", "1883"))
    received = Event()

    def on_message(payload: dict) -> None:
        print(f"MQTT received payload: {payload}")
        received.set()

    client = MqttClient(MqttConfig(host=host, port=port, qos=1, retain=False))

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
