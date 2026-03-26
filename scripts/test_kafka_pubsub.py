"""Kafka pub/sub smoke test (stabilized for consumer rebalance timing)."""
from __future__ import annotations

import threading
import time
import uuid
from threading import Event

from smart_messaging_core import KafkaClient, KafkaConfig


def main() -> None:
    topic = "smart.messaging.demo"
    received = Event()
    group_id = f"smart-messaging-core-demo-{uuid.uuid4().hex[:8]}"

    def on_message(payload: dict) -> None:
        print(f"Kafka received payload: {payload}")
        received.set()

    client = KafkaClient(
        KafkaConfig(
            bootstrap_servers="localhost:9092",
            group_id=group_id,
            auto_offset_reset="earliest",
        )
    )

    try:
        thread = threading.Thread(target=lambda: client.subscribe(topic, on_message), daemon=True)
        thread.start()

        # Wait for consumer group join/rebalance to settle before publishing.
        time.sleep(5.0)

        ok1 = client.publish(topic, {"message": "hello kafka #1"})
        time.sleep(1.0)
        ok2 = client.publish(topic, {"message": "hello kafka #2"})

        print(f"Kafka publish #1 returned: {ok1}")
        print(f"Kafka publish #2 returned: {ok2}")
        print(f"Kafka subscribe received: {received.wait(timeout=10)}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
