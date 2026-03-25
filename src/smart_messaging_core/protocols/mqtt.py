"""MQTT protocol client."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Callable

from smart_messaging_core.base import BaseProtocolClient, BaseProtocolConfig

LOGGER = logging.getLogger(__name__)


@dataclass
class MqttConfig(BaseProtocolConfig):
    host: str = "localhost"
    port: int = 1883
    qos: int = 1
    retain: bool = True
    client_id: str | None = None
    keepalive: int = 60
    auth_enabled: bool = False
    username: str | None = None
    password: str | None = None


class MqttClient(BaseProtocolClient):
    """MQTT client supporting both publish and subscribe."""

    supports_publish = True
    supports_subscribe = True
    config_type = MqttConfig

    def __init__(self, config: MqttConfig) -> None:
        super().__init__(config)
        self._client = None
        self._subscriptions: set[str] = set()

    def publish(self, channel: str, payload: dict[str, object]) -> bool:
        try:
            client = self._ensure_client(connect_async=False)
        except Exception as exc:  # pylint: disable=broad-except
            LOGGER.warning("MQTT publish client init failed: %s", exc)
            return False

        message = json.dumps(payload, ensure_ascii=False)
        result = client.publish(channel, message, qos=self._config.qos, retain=self._config.retain)
        if result.rc != 0:
            LOGGER.warning("MQTT publish failed (rc=%s)", result.rc)
            return False
        return True

    def subscribe(self, channel: str, handler: Callable[[dict[str, object]], None]) -> None:
        try:
            client = self._ensure_client(connect_async=True)
        except Exception as exc:  # pylint: disable=broad-except
            LOGGER.warning("MQTT subscribe client init failed: %s", exc)
            return
        client.message_callback_add(channel, self._build_message_handler(handler))
        self._subscriptions.add(channel)
        if getattr(client, "is_connected", lambda: False)():
            client.subscribe(channel, qos=self._config.qos)

    def _ensure_client(self, connect_async: bool):
        if self._client is not None:
            return self._client
        try:
            import paho.mqtt.client as mqtt  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError("Missing dependency: paho-mqtt") from exc
        client = mqtt.Client(client_id=self._config.client_id)
        _apply_auth(client, self._config)
        client.on_connect = self._handle_connect
        if connect_async:
            client.reconnect_delay_set(min_delay=1, max_delay=30)
            client.connect_async(self._config.host, self._config.port, keepalive=self._config.keepalive)
            client.loop_start()
        else:
            client.connect(self._config.host, self._config.port, keepalive=self._config.keepalive)
            client.loop_start()
        self._client = client
        return client


    def close(self) -> None:
        if self._client is None:
            return
        try:
            self._client.loop_stop()
        except Exception as exc:  # pylint: disable=broad-except
            LOGGER.debug("MQTT loop_stop failed: %s", exc)
        try:
            self._client.disconnect()
        except Exception as exc:  # pylint: disable=broad-except
            LOGGER.debug("MQTT disconnect failed: %s", exc)
        self._client = None

    def _handle_connect(self, client, userdata, flags, rc):  # noqa: ANN001
        _ = (userdata, flags)
        if rc != 0:
            LOGGER.warning("MQTT connect failed (rc=%s)", rc)
            return
        for channel in self._subscriptions:
            client.subscribe(channel, qos=self._config.qos)

    @staticmethod
    def _build_message_handler(handler: Callable[[dict[str, object]], None]):
        def _handle_message(client, userdata, msg):  # noqa: ANN001
            _ = (client, userdata)
            try:
                payload = json.loads(msg.payload.decode("utf-8") or "{}")
            except json.JSONDecodeError:
                LOGGER.debug("MQTT message ignored: invalid json")
                return
            if isinstance(payload, dict):
                handler(payload)

        return _handle_message


class MqttPublisher:
    """Compatibility wrapper for the legacy MQTT publish API."""

    def __init__(self, config: MqttConfig, topic: str) -> None:
        self._client = MqttClient(config)
        self._topic = topic

    def publish(self, payload: dict[str, object]) -> bool:
        return self._client.publish(self._topic, payload)


class MqttSubscriber:
    """Compatibility wrapper for the legacy MQTT subscribe API."""

    def __init__(
        self,
        config: MqttConfig,
        topic: str,
        on_message: Callable[[dict[str, object]], None],
    ) -> None:
        self._client = MqttClient(config)
        self._topic = topic
        self._on_message = on_message

    def start(self) -> None:
        self._client.subscribe(self._topic, self._on_message)


def _apply_auth(client, config: MqttConfig) -> None:  # noqa: ANN001
    if not config.auth_enabled:
        return
    if not config.username:
        raise ValueError("mqtt auth enabled but username is empty")
    client.username_pw_set(config.username, config.password)
