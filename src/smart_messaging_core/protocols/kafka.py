"""Kafka protocol client."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Callable

from smart_messaging_core.base import BaseProtocolClient, BaseProtocolConfig

LOGGER = logging.getLogger(__name__)


@dataclass
class KafkaConfig(BaseProtocolConfig):
    bootstrap_servers: str = "localhost:9092"
    client_id: str | None = None
    group_id: str | None = None
    auto_offset_reset: str = "latest"


class KafkaClient(BaseProtocolClient):
    """Kafka client supporting publish and subscribe."""

    supports_publish = True
    supports_subscribe = True
    config_type = KafkaConfig

    def publish(self, channel: str, payload: dict[str, Any]) -> bool:
        try:
            from kafka import KafkaProducer  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError("Missing dependency: kafka-python") from exc
        producer = KafkaProducer(
            bootstrap_servers=self._config.bootstrap_servers,
            client_id=self._config.client_id,
            value_serializer=lambda value: json.dumps(value, ensure_ascii=False).encode("utf-8"),
        )
        try:
            producer.send(channel, payload).get(timeout=5)
            return True
        finally:
            producer.close()

    def subscribe(self, channel: str, handler: Callable[[dict[str, Any]], None]) -> None:
        try:
            from kafka import KafkaConsumer  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError("Missing dependency: kafka-python") from exc
        consumer = KafkaConsumer(
            channel,
            bootstrap_servers=self._config.bootstrap_servers,
            client_id=self._config.client_id,
            group_id=self._config.group_id,
            auto_offset_reset=self._config.auto_offset_reset,
            value_deserializer=lambda value: json.loads(value.decode("utf-8") or "{}"),
        )
        for message in consumer:
            if isinstance(message.value, dict):
                handler(message.value)
