"""HTTP pub/sub smoke test using local webhook loopback via MessagingClient."""
from __future__ import annotations

import os
import time
from threading import Event

from smart_messaging_core import HttpConfig, MessagingClient, MessagingConfig, RouteConfig

ROUTE_KEY = "http_demo"


def main() -> None:
    listen_host = os.getenv("SMC_HTTP_LISTEN_HOST", "127.0.0.1")
    listen_port = int(os.getenv("SMC_HTTP_LISTEN_PORT", "9000"))
    endpoint = os.getenv("SMC_HTTP_ENDPOINT", "/smart-messaging-core/demo")
    timeout_seconds = float(os.getenv("SMC_HTTP_TIMEOUT_SECONDS", "3"))
    base_url = os.getenv("SMC_HTTP_BASE_URL", f"http://{listen_host}:{listen_port}")

    received = Event()

    def on_message(payload: dict) -> None:
        print(f"HTTP received payload: {payload}")
        received.set()

    client = MessagingClient(
        MessagingConfig(
            http=HttpConfig(
                base_url=base_url,
                listen_host=listen_host,
                listen_port=listen_port,
                timeout_seconds=timeout_seconds,
            ),
            routes={ROUTE_KEY: RouteConfig(backend="http", channel=endpoint)},
        )
    )

    try:
        client.subscribe(ROUTE_KEY, on_message)
        time.sleep(0.2)
        ok = client.publish(ROUTE_KEY, {"message": "hello http"})
        print(f"HTTP publish returned: {ok}")
        print(f"HTTP subscribe received: {received.wait(timeout=3)}")
    finally:
        client.close()


if __name__ == "__main__":
    main()
