"""Unified messaging client for multiple backends."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

from smart_messaging_core.protocols.http import HttpConfig
from smart_messaging_core.protocols.mqtt import MqttConfig
from smart_messaging_core.registry import PUBLISHERS, SUBSCRIBERS

LOGGER = logging.getLogger(__name__)


@dataclass
class MessagingConfig:
    publish_backend: str = "http"
    subscribe_backend: str = "mqtt"
    # degraded: log and continue; strict: raise on messaging errors
    failure_mode: str = "degraded"
    mqtt: MqttConfig = field(default_factory=MqttConfig)
    http: HttpConfig | None = None
    topic_routes: dict[str, str] = field(default_factory=dict)


class MessagingClient:
    def __init__(self, config: MessagingConfig) -> None:
        self._config = config
        self._publishers: dict[str, Any] = {}
        self._subscribers: dict[str, Any] = {}

    def publish(self, topic: str, payload: dict[str, Any]) -> bool:
        backend = self._config.publish_backend.lower()
        if backend == "none":
            return False
        try:
            entry = PUBLISHERS.get(backend)
            if entry is None:
                raise ValueError(f"Unsupported publish backend: {backend}")
            config_cls, publisher_cls = entry
            publisher_key = backend if backend != "mqtt" else topic
            publisher = self._publishers.get(publisher_key)
            if publisher is None:
                cfg = self._resolve_publish_config(backend, config_cls)
                if backend == "http":
                    publisher = publisher_cls(cfg, topic_routes=self._config.topic_routes)
                else:
                    publisher = publisher_cls(cfg, topic=topic)
                self._publishers[publisher_key] = publisher
            return publisher.publish(payload) if backend == "mqtt" else publisher.publish(topic, payload)
        except Exception as exc:  # pylint: disable=broad-except
            self._handle_error("publish", backend, exc)
            return False

    def subscribe(self, topic: str, handler: Callable[[dict[str, Any]], None]) -> None:
        backend = self._config.subscribe_backend.lower()
        if backend == "none":
            return
        try:
            entry = SUBSCRIBERS.get(backend)
            if entry is None:
                raise ValueError(f"Unsupported subscribe backend: {backend}")
            if topic in self._subscribers:
                return
            config_cls, subscriber_cls = entry
            cfg = self._resolve_subscribe_config(backend, config_cls)
            subscriber = subscriber_cls(cfg, topic=topic, on_message=handler)
            subscriber.start()
            self._subscribers[topic] = subscriber
        except Exception as exc:  # pylint: disable=broad-except
            self._handle_error("subscribe", backend, exc)
            return

    def _resolve_publish_config(self, backend: str, config_cls: type) -> Any:
        if backend == "mqtt":
            return self._config.mqtt
        if backend == "http":
            if self._config.http is None:
                raise ValueError("HTTP publish requires http config")
            return self._config.http
        raise ValueError(f"Missing publish config for backend: {backend}")

    def _resolve_subscribe_config(self, backend: str, config_cls: type) -> Any:
        if backend == "mqtt":
            return self._config.mqtt
        raise ValueError(f"Missing subscribe config for backend: {backend}")

    def _handle_error(self, action: str, backend: str, exc: Exception) -> None:
        mode = (self._config.failure_mode or "degraded").strip().lower()
        if mode == "strict":
            raise exc
        LOGGER.warning("Messaging %s failed (backend=%s, mode=%s): %s", action, backend, mode, exc)
