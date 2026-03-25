"""Protocol registry for smart_messaging_core."""
from __future__ import annotations

from typing import Any

from smart_messaging_core.protocols.http import HttpClient, HttpConfig
from smart_messaging_core.protocols.kafka import KafkaClient, KafkaConfig
from smart_messaging_core.protocols.mqtt import MqttClient, MqttConfig
from smart_messaging_core.protocols.redis import RedisClient, RedisConfig


CLIENTS: dict[str, tuple[str, type[Any], type[Any]]] = {
    "mqtt": ("mqtt", MqttConfig, MqttClient),
    "http": ("http", HttpConfig, HttpClient),
    "kafka": ("kafka", KafkaConfig, KafkaClient),
    "redis": ("redis", RedisConfig, RedisClient),
}
