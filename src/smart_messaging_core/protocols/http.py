"""HTTP protocol client."""
from __future__ import annotations

import json
import logging
import threading
import urllib.error
import urllib.request
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable

from smart_messaging_core.base import BaseProtocolClient, BaseProtocolConfig

LOGGER = logging.getLogger(__name__)


@dataclass
class HttpConfig(BaseProtocolConfig):
    base_url: str = ""
    timeout_seconds: int = 5
    listen_host: str = "0.0.0.0"
    listen_port: int = 9000


class HttpClient(BaseProtocolClient):
    """HTTP client supporting publish + webhook subscribe."""

    supports_publish = True
    supports_subscribe = True
    config_type = HttpConfig

    def __init__(self, config: HttpConfig) -> None:
        super().__init__(config)
        self._server: ThreadingHTTPServer | None = None
        self._server_thread: threading.Thread | None = None
        self._handlers: dict[str, Callable[[dict[str, Any]], None]] = {}

    @property
    def listening_port(self) -> int:
        if self._server is None:
            return self._config.listen_port
        return int(self._server.server_address[1])

    def publish(self, channel: str, payload: dict[str, Any]) -> bool:
        if not self._config.base_url:
            LOGGER.warning("HTTP publish failed: base_url is empty")
            return False
        path = channel if channel.startswith("/") else f"/{channel}"
        url = f"{self._config.base_url.rstrip('/')}{path}"
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self._config.timeout_seconds):
                return True
        except urllib.error.URLError as exc:
            LOGGER.warning("HTTP publish failed (%s): %s", url, exc)
            return False

    def subscribe(self, channel: str, handler: Callable[[dict[str, Any]], None]) -> None:
        path = channel if channel.startswith("/") else f"/{channel}"
        self._handlers[path] = handler
        self._ensure_server()

    def close(self) -> None:
        if self._server is None:
            return
        self._server.shutdown()
        self._server.server_close()
        if self._server_thread is not None:
            self._server_thread.join(timeout=2)
        self._server = None
        self._server_thread = None

    def _ensure_server(self) -> None:
        if self._server is not None:
            return

        owner = self

        class _WebhookHandler(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                callback = owner._handlers.get(self.path)
                if callback is None:
                    self.send_error(HTTPStatus.NOT_FOUND, "unknown path")
                    return

                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length)
                try:
                    payload = json.loads(body.decode("utf-8"))
                    if not isinstance(payload, dict):
                        raise ValueError("payload must be JSON object")
                except Exception as exc:  # pylint: disable=broad-except
                    LOGGER.warning("HTTP subscribe invalid payload (%s): %s", self.path, exc)
                    self.send_error(HTTPStatus.BAD_REQUEST, f"invalid payload: {exc}")
                    return

                try:
                    callback(payload)
                except Exception as exc:  # pylint: disable=broad-except
                    LOGGER.warning("HTTP subscribe callback failed (%s): %s", self.path, exc)
                    self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, "callback failed")
                    return

                self.send_response(HTTPStatus.ACCEPTED)
                self.end_headers()

            def log_message(self, format, *args):  # noqa: A003, ANN001
                LOGGER.debug("http-sub %s - %s", self.address_string(), format % args)

        self._server = ThreadingHTTPServer(
            (self._config.listen_host, self._config.listen_port),
            _WebhookHandler,
        )
        self._server_thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._server_thread.start()
        LOGGER.info(
            "HTTP subscribe server listening on %s:%s",
            self._config.listen_host,
            self.listening_port,
        )


class HttpPublisher:
    """Compatibility wrapper for the legacy publish-only HTTP API."""

    def __init__(self, config: HttpConfig, topic_routes: dict[str, str] | None = None) -> None:
        self._client = HttpClient(config)
        self._topic_routes = topic_routes or {}

    def publish(self, topic: str, payload: dict[str, Any]) -> bool:
        channel = self._topic_routes.get(topic, topic)
        return self._client.publish(channel, payload)
