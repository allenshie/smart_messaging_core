"""Unified messaging client for multiple backends."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable

from smart_messaging_core.protocols.http import HttpConfig, HttpPublisher
from smart_messaging_core.protocols.mqtt import MqttConfig, MqttPublisher, MqttSubscriber

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
            if backend == "mqtt":
                publisher = self._publishers.get(topic)
                if publisher is None:
                    publisher = MqttPublisher(self._config.mqtt, topic=topic)
                    self._publishers[topic] = publisher
                return publisher.publish(payload)
            if backend == "http":
                publisher = self._publishers.get("http")
                if publisher is None:
                    if self._config.http is None:
                        raise ValueError("HTTP publish requires http config")
                    publisher = HttpPublisher(self._config.http, topic_routes=self._config.topic_routes)
                    self._publishers["http"] = publisher
                return publisher.publish(topic, payload)
            raise ValueError(f"Unsupported publish backend: {backend}")
        except Exception as exc:  # pylint: disable=broad-except
            self._handle_error("publish", backend, exc)
            return False

    def subscribe(self, topic: str, handler: Callable[[dict[str, Any]], None]) -> None:
        backend = self._config.subscribe_backend.lower()
        if backend == "none":
            return
        try:
            if backend != "mqtt":
                raise ValueError(f"Unsupported subscribe backend: {backend}")
            if topic in self._subscribers:
                return
            subscriber = MqttSubscriber(self._config.mqtt, topic=topic, on_message=handler)
            subscriber.start()
            self._subscribers[topic] = subscriber
        except Exception as exc:  # pylint: disable=broad-except
            self._handle_error("subscribe", backend, exc)
            return

    def _handle_error(self, action: str, backend: str, exc: Exception) -> None:
        mode = (self._config.failure_mode or "degraded").strip().lower()
        if mode == "strict":
            raise exc
        LOGGER.warning("Messaging %s failed (backend=%s, mode=%s): %s", action, backend, mode, exc)
