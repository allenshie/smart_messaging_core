# MQTT 使用說明

## 支援能力

- publish
- subscribe

## 推薦使用方式

```python
from smart_messaging_core import MessagingClient, MessagingConfig, MqttConfig, RouteConfig

cfg = MessagingConfig(
    mqtt=MqttConfig(host="localhost", port=1883, qos=1, retain=True),
    routes={
        "phase_publish": RouteConfig(backend="mqtt", channel="integration/phase"),
        "edge_events": RouteConfig(backend="mqtt", channel="edge/events"),
    },
)

client = MessagingClient(cfg)
client.publish("phase_publish", {"phase": "working_stage_1"})
client.subscribe("edge_events", lambda payload: print(payload))
```

## 主要參數

### `MqttConfig`

- `host`
  - 範例值：`"localhost"`
  - MQTT broker host
- `port`
  - 範例值：`1883`
  - MQTT broker port
- `qos`
  - 範例值：`1`
  - publish / subscribe QoS
- `retain`
  - 範例值：`True`
  - publish retain flag
- `client_id`
  - 範例值：`"edge-app-01"`
  - 可選的 MQTT client id
- `keepalive`
  - 範例值：`60`
  - keepalive 秒數
- `auth_enabled`
  - 範例值：`True`
  - 是否啟用帳密登入
- `username` / `password`
  - MQTT broker 帳號密碼

### `RouteConfig`

- `backend`
  - 範例值：`"mqtt"`
- `channel`
  - 範例值：`"integration/phase"`
  - MQTT topic 名稱

## 帳密（可選）

```python
cfg = MessagingConfig(
    mqtt=MqttConfig(
        host="localhost",
        port=1883,
        qos=1,
        retain=True,
        auth_enabled=True,
        username="mqtt_user",
        password="mqtt_password",
    ),
    routes={
        "phase_publish": RouteConfig(backend="mqtt", channel="integration/phase"),
    },
)
```

## 測試腳本

```bash
source .venv/bin/activate
python scripts/test_mqtt_pubsub.py
```

## Docker image 版本參考

- image：`eclipse-mosquitto:2.0`

啟動指令：

```bash
docker run -d --name smart-msg-mqtt -p 1883:1883 eclipse-mosquitto:2.0
```
