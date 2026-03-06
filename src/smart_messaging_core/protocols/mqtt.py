"""MQTT publisher/subscriber helpers."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Callable

LOGGER = logging.getLogger(__name__)


@dataclass
class MqttConfig:
    host: str = "localhost"
    port: int = 1883
    qos: int = 1
    retain: bool = True
    client_id: str | None = None
    keepalive: int = 60
    auth_enabled: bool = False
    username: str | None = None
    password: str | None = None


class MqttPublisher:
    def __init__(self, config: MqttConfig, topic: str) -> None:
        self._config = config
        self._topic = topic
        self._client = None

    def publish(self, payload: dict[str, Any]) -> bool:
        try:
            self._ensure_client()
        except Exception as exc:  # pylint: disable=broad-except
            LOGGER.warning("MQTT publisher init failed: %s", exc)
            return False

        message = json.dumps(payload, ensure_ascii=False)
        result = self._client.publish(self._topic, message, qos=self._config.qos, retain=self._config.retain)
        if result.rc != 0:
            LOGGER.warning("MQTT publish failed (rc=%s)", result.rc)
            return False
        return True

    def _ensure_client(self) -> None:
        if self._client is not None:
            return
        try:
            import paho.mqtt.client as mqtt  # type: ignore
        except ModuleNotFoundError as exc:
            raise RuntimeError("Missing dependency: paho-mqtt") from exc
        client = mqtt.Client(client_id=self._config.client_id)
        _apply_auth(client, self._config)
        client.connect(self._config.host, self._config.port, keepalive=self._config.keepalive)
        client.loop_start()
        self._client = client


class MqttSubscriber:
    def __init__(
        self,
        config: MqttConfig,
        topic: str,
        on_message: Callable[[dict[str, Any]], None],
    ) -> None:
        self._config = config
        self._topic = topic
        self._on_message = on_message
        self._client = None

    def start(self) -> None:
        try:
            import paho.mqtt.client as mqtt  # type: ignore
        except ModuleNotFoundError as exc:
            LOGGER.warning("MQTT subscriber disabled: %s", exc)
            return
        client = mqtt.Client(client_id=self._config.client_id)
        try:
            _apply_auth(client, self._config)
        except ValueError as exc:
            LOGGER.warning("MQTT subscriber auth config invalid: %s", exc)
            return
        client.on_connect = self._handle_connect
        client.on_message = self._handle_message
        # Do not crash the service if the broker is temporarily unavailable.
        try:
            client.reconnect_delay_set(min_delay=1, max_delay=30)
            client.connect_async(self._config.host, self._config.port, keepalive=self._config.keepalive)
            client.loop_start()
            self._client = client
        except Exception as exc:  # pylint: disable=broad-except
            LOGGER.warning("MQTT subscriber start failed: %s", exc)
            return

    def _handle_connect(self, client, userdata, flags, rc):  # noqa: ANN001
        _ = (userdata, flags)
        if rc != 0:
            LOGGER.warning("MQTT connect failed (rc=%s)", rc)
            return
        client.subscribe(self._topic, qos=self._config.qos)

    def _handle_message(self, client, userdata, msg):  # noqa: ANN001
        _ = (client, userdata)
        try:
            payload = json.loads(msg.payload.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            LOGGER.debug("MQTT message ignored: invalid json")
            return
        if not isinstance(payload, dict):
            return
        self._on_message(payload)


def _apply_auth(client, config: MqttConfig) -> None:  # noqa: ANN001
    if not config.auth_enabled:
        return
    if not config.username:
        raise ValueError("mqtt auth enabled but username is empty")
    client.username_pw_set(config.username, config.password)
