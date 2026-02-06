"""Protocol registry for smart_messaging_core."""
from __future__ import annotations

from typing import Dict, Tuple, Type, Any

from smart_messaging_core.protocols.http import HttpConfig, HttpPublisher
from smart_messaging_core.protocols.mqtt import MqttConfig, MqttPublisher, MqttSubscriber


PublisherEntry = Tuple[Type[Any], Type[Any]]
SubscriberEntry = Tuple[Type[Any], Type[Any]]


PUBLISHERS: Dict[str, PublisherEntry] = {
    "mqtt": (MqttConfig, MqttPublisher),
    "http": (HttpConfig, HttpPublisher),
}

SUBSCRIBERS: Dict[str, SubscriberEntry] = {
    "mqtt": (MqttConfig, MqttSubscriber),
}
