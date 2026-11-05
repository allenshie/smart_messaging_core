"""MQTT 連線行為測試：以真實 paho client 連本機的最小 broker。"""
from __future__ import annotations

import json
import socket
import threading
import time
from unittest import TestCase, mock

from smart_messaging_core.client import MessagingClient, MessagingConfig, RouteConfig
from smart_messaging_core.protocols.http import HttpConfig
from smart_messaging_core.protocols.mqtt import MqttClient, MqttConfig

LOGGER_NAME = "smart_messaging_core.protocols.mqtt"
_CONNECT, _PUBLISH, _SUBSCRIBE, _PINGREQ = 1, 3, 8, 12


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _wait_until(predicate, timeout: float = 6.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.02)
    return predicate()


class FakeBroker:
    """只實作測試需要的 MQTT 3.1.1 封包。"""

    def __init__(self, port: int) -> None:
        self.published: list[dict] = []
        self.subscribed: list[str] = []
        self._connections: list[socket.socket] = []
        self._server = socket.create_server(("127.0.0.1", port))
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def stop(self) -> None:
        self._server.close()
        for connection in self._connections:
            try:
                connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            connection.close()

    def _accept_loop(self) -> None:
        while True:
            try:
                connection, _ = self._server.accept()
            except OSError:
                return
            self._connections.append(connection)
            threading.Thread(target=self._serve, args=(connection,), daemon=True).start()

    def _serve(self, connection: socket.socket) -> None:
        try:
            while True:
                header = self._read_exact(connection, 1)[0]
                self._handle(connection, header, self._read_packet_body(connection))
        except OSError:
            pass

    def _handle(self, connection: socket.socket, header: int, body: bytes) -> None:
        packet_type = header >> 4
        if packet_type == _CONNECT:
            connection.sendall(b"\x20\x02\x00\x00")
        elif packet_type == _PUBLISH:
            qos = (header >> 1) & 0b11
            topic_length = int.from_bytes(body[:2], "big")
            offset = 2 + topic_length
            if qos:
                connection.sendall(b"\x40\x02" + body[offset : offset + 2])
                offset += 2
            self.published.append(json.loads(body[offset:]))
        elif packet_type == _SUBSCRIBE:
            topic_length = int.from_bytes(body[2:4], "big")
            self.subscribed.append(body[4 : 4 + topic_length].decode())
            connection.sendall(b"\x90\x03" + body[:2] + b"\x00")
        elif packet_type == _PINGREQ:
            connection.sendall(b"\xd0\x00")

    def _read_packet_body(self, connection: socket.socket) -> bytes:
        length, shift = 0, 0
        while True:
            byte = self._read_exact(connection, 1)[0]
            length |= (byte & 0x7F) << shift
            shift += 7
            if not byte & 0x80:
                return self._read_exact(connection, length)

    @staticmethod
    def _read_exact(connection: socket.socket, size: int) -> bytes:
        chunks = b""
        while len(chunks) < size:
            chunk = connection.recv(size - len(chunks))
            if not chunk:
                raise OSError("connection closed")
            chunks += chunk
        return chunks


class UnreachableBrokerTests(TestCase):
    """模擬主機連不到：TCP 連線要等到逾時才失敗。"""

    def setUp(self) -> None:
        def slow_timeout(*_args, **_kwargs):
            time.sleep(1.0)
            raise TimeoutError("timed out")

        patcher = mock.patch("socket.create_connection", side_effect=slow_timeout)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.client = MqttClient(MqttConfig(host="192.0.2.1", port=1883, qos=0))
        self.addCleanup(self.client.close)

    def test_publish_does_not_wait_for_connection(self) -> None:
        started = time.monotonic()
        results = [self.client.publish("edge/events", {"seq": seq}) for seq in range(3)]
        elapsed = time.monotonic() - started

        self.assertEqual(results, [False, False, False])
        self.assertLess(elapsed, 0.5)

    def test_connect_failure_log_names_the_broker(self) -> None:
        with self.assertLogs(LOGGER_NAME, level="WARNING") as captured:
            self.client.publish("edge/events", {"seq": 1})
            self.assertTrue(
                _wait_until(lambda: "192.0.2.1:1883" in "\n".join(captured.output), timeout=3.0)
            )


class LateBrokerTests(TestCase):
    """broker 在 client 之後才啟動，之後還可能再中斷。"""

    def setUp(self) -> None:
        self.port = _free_port()

    def _client(self, **config) -> MqttClient:
        client = MqttClient(MqttConfig(host="127.0.0.1", port=self.port, **config))
        self.addCleanup(client.close)
        return client

    def _start_broker(self) -> FakeBroker:
        broker = FakeBroker(self.port)
        self.addCleanup(broker.stop)
        return broker

    def test_publish_delivers_after_broker_starts(self) -> None:
        client = self._client(qos=0)
        self.assertFalse(client.publish("edge/events", {"seq": "before"}))

        broker = self._start_broker()

        def publish_arrived() -> bool:
            client.publish("edge/events", {"seq": "after"})
            return {"seq": "after"} in broker.published

        self.assertTrue(_wait_until(publish_arrived))
        self.assertNotIn({"seq": "before"}, broker.published)

    def test_subscription_is_registered_after_broker_starts(self) -> None:
        client = self._client(qos=0)
        client.subscribe("integration/phase", lambda _payload: None)

        broker = self._start_broker()

        self.assertTrue(_wait_until(lambda: "integration/phase" in broker.subscribed))

    def test_is_connected_follows_broker_availability(self) -> None:
        client = self._client(qos=0)
        self.assertFalse(client.is_connected())

        client.publish("edge/events", {"seq": 1})
        self.assertFalse(client.is_connected())

        broker = self._start_broker()
        self.assertTrue(_wait_until(client.is_connected))

        broker.stop()
        self.assertTrue(_wait_until(lambda: not client.is_connected()))

    def test_qos1_queue_is_bounded_while_disconnected(self) -> None:
        client = self._client(qos=1, retain=False, max_queued_messages=2)
        for seq in range(5):
            client.publish("edge/events", {"seq": seq})

        broker = self._start_broker()
        self.assertTrue(_wait_until(lambda: len(broker.published) >= 2))
        time.sleep(0.3)

        self.assertEqual(broker.published, [{"seq": 0}, {"seq": 1}])


class MessagingClientConnectionTests(TestCase):
    def setUp(self) -> None:
        self.port = _free_port()
        self.client = MessagingClient(
            MessagingConfig(
                mqtt=MqttConfig(host="127.0.0.1", port=self.port, qos=0),
                http=HttpConfig(base_url="http://localhost:8080"),
                routes={
                    "events": RouteConfig(backend="mqtt", channel="edge/events"),
                    "api": RouteConfig(backend="http", channel="/edge/events"),
                },
            )
        )
        self.addCleanup(self.client.close)

    def test_reports_mqtt_route_connection(self) -> None:
        self.assertIs(self.client.is_connected("events"), False)

        self.client.publish("events", {"seq": 1})
        broker = FakeBroker(self.port)
        self.addCleanup(broker.stop)

        self.assertTrue(_wait_until(lambda: self.client.is_connected("events") is True))

    def test_backend_without_connection_state_returns_none(self) -> None:
        self.assertIsNone(self.client.is_connected("api"))

    def test_unknown_route_returns_none_in_degraded_mode(self) -> None:
        self.assertIsNone(self.client.is_connected("missing"))
