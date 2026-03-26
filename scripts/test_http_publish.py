"""HTTP pub/sub smoke test using local webhook loopback."""
from __future__ import annotations

import time
from threading import Event

from smart_messaging_core import HttpClient, HttpConfig


def main() -> None:
    received = Event()

    def on_message(payload: dict) -> None:
        print(f"HTTP received payload: {payload}")
        received.set()

    cfg = HttpConfig(
        base_url="http://127.0.0.1:9000",
        listen_host="127.0.0.1",
        listen_port=9000,
        timeout_seconds=3,
    )
    client = HttpClient(cfg)

    try:
        client.subscribe("/smart-messaging-core/demo", on_message)
        time.sleep(0.2)
        ok = client.publish("/smart-messaging-core/demo", {"message": "hello http"})
        print(f"HTTP publish returned: {ok}")
        print(f"HTTP subscribe received: {received.wait(timeout=3)}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
