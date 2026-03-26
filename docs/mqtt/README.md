# MQTT 使用說明

## 支援能力

- publish
- subscribe

## 最小設定

```python
from smart_messaging_core import MqttConfig, MqttClient

cfg = MqttConfig(host="localhost", port=1883, qos=1, retain=True)
client = MqttClient(cfg)
```

## Publish

```python
client.publish("integration/phase", {"phase": "working_stage_1"})
```

## Subscribe

```python
client.subscribe("integration/phase", lambda payload: print(payload))
```

## 帳密（可選）

```python
cfg = MqttConfig(
    host="localhost",
    port=1883,
    qos=1,
    retain=True,
    auth_enabled=True,
    username="mqtt_user",
    password="mqtt_password",
)
```

## 測試腳本

```bash
source .venv/bin/activate
python scripts/test_mqtt_pubsub.py  # subscribe + publish + close
```

## Docker image 版本參考

- image：`eclipse-mosquitto:2.0`

啟動指令：

```bash
docker run -d --name smart-msg-mqtt -p 1883:1883 eclipse-mosquitto:2.0
```
