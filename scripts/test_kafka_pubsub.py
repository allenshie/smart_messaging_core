"""Kafka pub/sub smoke test via MessagingClient."""
from __future__ import annotations

import os
import threading
import time
import uuid
from threading import Event

from smart_messaging_core import KafkaConfig, MessagingClient, MessagingConfig, RouteConfig

ROUTE_KEY = "kafka_demo"


def main() -> None:
    channel = os.getenv("SMC_KAFKA_TOPIC", "smart.messaging.demo")
    bootstrap_servers = os.getenv("SMC_KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092")
    warmup_seconds = float(os.getenv("SMC_KAFKA_WARMUP_SECONDS", "5"))
    received = Event()
    group_id = os.getenv("SMC_KAFKA_GROUP_ID", f"smart-messaging-core-demo-{uuid.uuid4().hex[:8]}")

    def on_message(payload: dict) -> None:
        print(f"Kafka received payload: {payload}")
        received.set()

    client = MessagingClient(
        MessagingConfig(
            kafka=KafkaConfig(
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                auto_offset_reset="earliest",
            ),
            routes={ROUTE_KEY: RouteConfig(backend="kafka", channel=channel)},
        )
    )

    try:
        thread = threading.Thread(target=lambda: client.subscribe(ROUTE_KEY, on_message), daemon=True)
        thread.start()
        time.sleep(warmup_seconds)
        ok1 = client.publish(ROUTE_KEY, {"message": "hello kafka #1"})
        time.sleep(1.0)
        ok2 = client.publish(ROUTE_KEY, {"message": "hello kafka #2"})
        print(f"Kafka publish #1 returned: {ok1}")
        print(f"Kafka publish #2 returned: {ok2}")
        print(f"Kafka subscribe received: {received.wait(timeout=10)}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
