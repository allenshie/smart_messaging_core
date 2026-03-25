from dataclasses import dataclass
from unittest import TestCase
from unittest.mock import patch

from smart_messaging_core.base import BaseProtocolClient, BaseProtocolConfig
from smart_messaging_core.client import MessagingClient, MessagingConfig, RouteConfig


@dataclass
class DummyConfig(BaseProtocolConfig):
    value: str = "dummy"


class DummyClient(BaseProtocolClient):
    supports_publish = True
    supports_subscribe = True
    config_type = DummyConfig

    def __init__(self, config: DummyConfig) -> None:
        super().__init__(config)
        self.published: list[tuple[str, dict]] = []
        self.subscribed: list[str] = []
        self.closed = False

    def publish(self, channel: str, payload: dict) -> bool:
        self.published.append((channel, payload))
        return True

    def subscribe(self, channel: str, handler) -> None:  # noqa: ANN001
        self.subscribed.append(channel)

    def close(self) -> None:
        self.closed = True


class MessagingClientRouteTests(TestCase):
    def test_routes_publish_and_subscribe(self) -> None:
        with patch(
            "smart_messaging_core.client.CLIENTS",
            {"dummy": ("dummy", DummyConfig, DummyClient)},
        ):
            cfg = MessagingConfig(
                routes={
                    "phase_publish": RouteConfig(backend="dummy", channel="integration/phase"),
                    "edge_events": RouteConfig(backend="dummy", channel="edge/events"),
                },
            )
            cfg.dummy = DummyConfig()  # type: ignore[attr-defined]
            client = MessagingClient(cfg)

            self.assertTrue(client.publish("phase_publish", {"phase": "working"}))
            client.subscribe("edge_events", lambda payload: payload)

            dummy = client._clients["dummy"]  # noqa: SLF001
            self.assertEqual(dummy.published, [("integration/phase", {"phase": "working"})])
            self.assertEqual(dummy.subscribed, ["edge/events"])

    def test_close_closes_all_created_protocol_clients(self) -> None:
        with patch(
            "smart_messaging_core.client.CLIENTS",
            {"dummy": ("dummy", DummyConfig, DummyClient)},
        ):
            cfg = MessagingConfig(routes={"phase_publish": RouteConfig(backend="dummy", channel="phase")})
            cfg.dummy = DummyConfig()  # type: ignore[attr-defined]
            client = MessagingClient(cfg)
            client.publish("phase_publish", {"x": 1})

            dummy = client._clients["dummy"]  # noqa: SLF001
            self.assertFalse(dummy.closed)
            client.close()
            self.assertTrue(dummy.closed)
            self.assertEqual(client._clients, {})  # noqa: SLF001
