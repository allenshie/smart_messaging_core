"""Redis pub/sub smoke test."""
from __future__ import annotations

import threading
import time
from threading import Event

from smart_messaging_core import RedisClient, RedisConfig


def main() -> None:
    channel = "smart-messaging-core:demo"
    received = Event()

    def on_message(payload: dict) -> None:
        print(f"Redis received payload: {payload}")
        received.set()

    client = RedisClient(RedisConfig(host="localhost", port=6379, db=0))

    try:
        thread = threading.Thread(target=lambda: client.subscribe(channel, on_message), daemon=True)
        thread.start()
        time.sleep(0.5)
        ok = client.publish(channel, {"message": "hello redis"})
        print(f"Redis publish returned: {ok}")
        print(f"Redis subscribe received: {received.wait(timeout=5)}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
