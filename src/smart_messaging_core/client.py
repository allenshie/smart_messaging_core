"""Route-based unified messaging client."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

from smart_messaging_core.protocols.http import HttpConfig
from smart_messaging_core.protocols.kafka import KafkaConfig
from smart_messaging_core.protocols.mqtt import MqttConfig
from smart_messaging_core.protocols.redis import RedisConfig
from smart_messaging_core.registry import CLIENTS

LOGGER = logging.getLogger(__name__)


@dataclass
class RouteConfig:
    backend: str
    channel: str


@dataclass
class MessagingConfig:
    failure_mode: str = "degraded"
    mqtt: MqttConfig = field(default_factory=MqttConfig)
    http: HttpConfig | None = None
    kafka: KafkaConfig | None = None
    redis: RedisConfig | None = None
    routes: dict[str, RouteConfig] = field(default_factory=dict)


class MessagingClient:
    """Facade that routes publish/subscribe calls to protocol-specific clients."""

    def __init__(self, config: MessagingConfig) -> None:
        self._config = config
        self._clients: dict[str, Any] = {}

    def publish(self, route_key: str, payload: dict[str, Any]) -> bool:
        try:
            backend, channel = self._resolve_route(route_key)
            client = self._get_client(backend)
            if not getattr(client, "supports_publish", False):
                raise ValueError(f"Backend {backend} does not support publish")
            return client.publish(channel, payload)
        except Exception as exc:  # pylint: disable=broad-except
            self._handle_error("publish", route_key, exc)
            return False

    def subscribe(self, route_key: str, handler: Callable[[dict[str, Any]], None]) -> None:
        try:
            backend, channel = self._resolve_route(route_key)
            client = self._get_client(backend)
            if not getattr(client, "supports_subscribe", False):
                raise ValueError(f"Backend {backend} does not support subscribe")
            client.subscribe(channel, handler)
        except Exception as exc:  # pylint: disable=broad-except
            self._handle_error("subscribe", route_key, exc)

    def close(self) -> None:
        for backend, client in list(self._clients.items()):
            try:
                close_fn = getattr(client, "close", None)
                if callable(close_fn):
                    close_fn()
            except Exception as exc:  # pylint: disable=broad-except
                LOGGER.warning("Messaging close failed (backend=%s): %s", backend, exc)
        self._clients.clear()

    def _resolve_route(self, route_key: str) -> tuple[str, str]:
        route = self._config.routes.get(route_key)
        if route is None:
            raise ValueError(f"Unknown route: {route_key}")
        return route.backend, route.channel

    def _get_client(self, backend: str):
        key = (backend or "").strip().lower()
        client = self._clients.get(key)
        if client is not None:
            return client
        entry = CLIENTS.get(key)
        if entry is None:
            raise ValueError(f"Unsupported backend: {backend}")
        config_attr, config_cls, client_cls = entry
        cfg = getattr(self._config, config_attr, None)
        if cfg is None:
            raise ValueError(f"Missing config for backend: {backend}")
        if not isinstance(cfg, config_cls):
            raise TypeError(
                f"Config for backend {backend} must be {config_cls.__name__}, got {type(cfg).__name__}"
            )
        client = client_cls(cfg)
        self._clients[key] = client
        return client

    def _handle_error(self, action: str, route_key: str, exc: Exception) -> None:
        mode = (self._config.failure_mode or "degraded").strip().lower()
        if mode == "strict":
            raise exc
        LOGGER.warning("Messaging %s failed (route=%s, mode=%s): %s", action, route_key, mode, exc)
