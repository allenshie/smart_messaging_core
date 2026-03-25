import json
import threading
import urllib.request
from unittest import TestCase

from smart_messaging_core.base import BaseProtocolConfig
from smart_messaging_core.client import MessagingClient, MessagingConfig, RouteConfig
from smart_messaging_core.protocols.http import HttpClient, HttpConfig
from smart_messaging_core.protocols.mqtt import MqttClient, MqttConfig


class WrongConfig(BaseProtocolConfig):
    pass


class ProtocolValidationTests(TestCase):
    def test_mqtt_client_rejects_wrong_config_type(self) -> None:
        with self.assertRaises(TypeError):
            MqttClient(WrongConfig())  # type: ignore[arg-type]

    def test_http_client_rejects_wrong_config_type(self) -> None:
        with self.assertRaises(TypeError):
            HttpClient(WrongConfig())  # type: ignore[arg-type]

    def test_messaging_client_strict_mode_raises_for_unsupported_backend(self) -> None:
        client = MessagingClient(
            MessagingConfig(
                failure_mode="strict",
                mqtt=MqttConfig(),
                http=HttpConfig(base_url="http://localhost:8080"),
                routes={"phase_publish": RouteConfig(backend="unsupported", channel="/phase")},
            )
        )
        with self.assertRaises(ValueError):
            client.publish("phase_publish", {"x": 1})

    def test_messaging_client_strict_mode_raises_for_unknown_route(self) -> None:
        client = MessagingClient(
            MessagingConfig(
                failure_mode="strict",
                mqtt=MqttConfig(),
                routes={"edge_events": RouteConfig(backend="mqtt", channel="edge/events")},
            )
        )
        with self.assertRaises(ValueError):
            client.publish("unknown_route", {"x": 1})

    def test_http_client_subscribe_starts_local_server(self) -> None:
        received: dict | None = None
        event = threading.Event()

        cfg = HttpConfig(listen_host="127.0.0.1", listen_port=0)
        client = HttpClient(cfg)

        def _handler(payload: dict) -> None:
            nonlocal received
            received = payload
            event.set()

        client.subscribe("/edge/events", _handler)
        port = client.listening_port

        req = urllib.request.Request(
            f"http://127.0.0.1:{port}/edge/events",
            data=json.dumps({"camera_id": "cam01"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=2):
            pass

        self.assertTrue(event.wait(timeout=2))
        self.assertEqual(received, {"camera_id": "cam01"})
        client.close()
