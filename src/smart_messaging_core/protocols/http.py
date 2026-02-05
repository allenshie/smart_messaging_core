"""HTTP publish helper."""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

LOGGER = logging.getLogger(__name__)


@dataclass
class HttpConfig:
    base_url: str
    timeout_seconds: int = 5


class HttpPublisher:
    def __init__(self, config: HttpConfig, topic_routes: dict[str, str] | None = None) -> None:
        self._config = config
        self._topic_routes = topic_routes or {}

    def publish(self, topic: str, payload: dict[str, Any]) -> bool:
        path = self._topic_routes.get(topic, topic)
        if not path.startswith("/"):
            path = f"/{path}"
        url = f"{self._config.base_url.rstrip('/')}{path}"
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self._config.timeout_seconds):
                return True
        except urllib.error.URLError as exc:
            LOGGER.warning("HTTP publish failed (%s): %s", url, exc)
            return False
