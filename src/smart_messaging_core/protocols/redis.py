"""Redis protocol client."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable

from smart_messaging_core.base import BaseProtocolClient, BaseProtocolConfig


@dataclass
class RedisConfig(BaseProtocolConfig):
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    username: str | None = None
    password: str | None = None


class RedisClient(BaseProtocolClient):
    """Redis pub/sub client."""

    supports_publish = True
    supports_subscribe = True
    config_type = RedisConfig

    def publish(self, channel: str, payload: dict[str, object]) -> bool:
        client = self._build_client()
        return client.publish(channel, json.dumps(payload, ensure_ascii=False)) > 0

    def subscribe(self, channel: str, handler: Callable[[dict[str, object]], None]) -> None:
        client = self._build_client()
        pubsub = client.pubsub()
        pubsub.subscribe(channel)
        for message in pubsub.listen():
            if message.get("type") != "message":
                continue
            data = message.get("data")
            if isinstance(data, bytes):
                payload = json.loads(data.decode("utf-8") or "{}")
                if isinstance(payload, dict):
                    handler(payload)

    def _build_client(self):
        try:
            import redis  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError("Missing dependency: redis") from exc
        return redis.Redis(
            host=self._config.host,
            port=self._config.port,
            db=self._config.db,
            username=self._config.username,
            password=self._config.password,
            decode_responses=False,
        )
