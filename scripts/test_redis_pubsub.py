"""Redis pub/sub smoke test via MessagingClient."""
from __future__ import annotations

import os
import threading
import time
from threading import Event

from smart_messaging_core import MessagingClient, MessagingConfig, RedisConfig, RouteConfig

ROUTE_KEY = "redis_demo"


def main() -> None:
    channel = os.getenv("SMC_REDIS_CHANNEL", "smart-messaging-core:demo")
    host = os.getenv("SMC_REDIS_HOST", "127.0.0.1")
    port = int(os.getenv("SMC_REDIS_PORT", "6379"))
    db = int(os.getenv("SMC_REDIS_DB", "0"))
    received = Event()

    def on_message(payload: dict) -> None:
        print(f"Redis received payload: {payload}")
        received.set()

    client = MessagingClient(
        MessagingConfig(
            redis=RedisConfig(host=host, port=port, db=db),
            routes={ROUTE_KEY: RouteConfig(backend="redis", channel=channel)},
        )
    )

    try:
        thread = threading.Thread(target=lambda: client.subscribe(ROUTE_KEY, on_message), daemon=True)
        thread.start()
        time.sleep(0.5)
        ok = client.publish(ROUTE_KEY, {"message": "hello redis"})
        print(f"Redis publish returned: {ok}")
        print(f"Redis subscribe received: {received.wait(timeout=5)}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
