# MQTT 使用範例

## Publisher

```python
from smart_messaging_core import MqttConfig, MqttPublisher

cfg = MqttConfig(host="localhost", port=1883, qos=1, retain=True)
publisher = MqttPublisher(cfg, topic="integration/phase")

publisher.publish({"phase": "working_stage_1"})
```

## Subscriber

```python
from smart_messaging_core import MqttConfig, MqttSubscriber

cfg = MqttConfig(host="localhost", port=1883, qos=1, retain=True)

subscriber = MqttSubscriber(
    cfg,
    topic="integration/phase",
    on_message=lambda payload: print(payload),
)
subscriber.start()
```
