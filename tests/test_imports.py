def test_imports() -> None:
    from smart_messaging_core import (  # noqa: F401
        MessagingClient,
        MessagingConfig,
        MqttConfig,
        MqttPublisher,
        MqttSubscriber,
        HttpConfig,
        HttpPublisher,
    )
