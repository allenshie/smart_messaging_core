"""MQTT pub/sub smoke test via MessagingClient."""
from __future__ import annotations

import os
import time
from threading import Event

from smart_messaging_core import MessagingClient, MessagingConfig, MqttConfig, RouteConfig

ROUTE_KEY = "mqtt_demo"


def main() -> None:
    channel = os.getenv("SMC_MQTT_TOPIC", "smart-messaging-core/demo")
    host = os.getenv("SMC_MQTT_HOST", "127.0.0.1")
    port = int(os.getenv("SMC_MQTT_PORT", "1883"))
    received = Event()

    def on_message(payload: dict) -> None:
        print(f"MQTT received payload: {payload}")
        received.set()

    client = MessagingClient(
        MessagingConfig(
            mqtt=MqttConfig(host=host, port=port, qos=1, retain=False),
            routes={ROUTE_KEY: RouteConfig(backend="mqtt", channel=channel)},
        )
    )

    try:
        client.subscribe(ROUTE_KEY, on_message)
        time.sleep(0.5)
        ok = client.publish(ROUTE_KEY, {"message": "hello mqtt"})
        print(f"MQTT publish returned: {ok}")
        print(f"MQTT subscribe received: {received.wait(timeout=5)}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
