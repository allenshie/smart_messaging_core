# 通訊介面

`smart_messaging_core` 提供統一的 `MessagingClient`，由 route 設定選擇實際協議與 channel。

## 發佈與版本

- 正式 PyPI：`smart-messaging-core==0.1.1`
- 套件頁面：<https://pypi.org/project/smart-messaging-core/>

安裝：

```bash
pip install smart-messaging-core==0.1.1
```

## Route-based 使用範例

```python
from smart_messaging_core import (
    MessagingClient,
    MessagingConfig,
    MqttConfig,
    HttpConfig,
    RouteConfig,
)

cfg = MessagingConfig(
    mqtt=MqttConfig(host="localhost", port=1883, qos=1, retain=True),
    http=HttpConfig(base_url="http://localhost:8080", listen_host="0.0.0.0", listen_port=9000),
    routes={
        "phase_publish": RouteConfig(backend="http", channel="/phase"),
        "board_command": RouteConfig(backend="mqtt", channel="board/command"),
        "edge_events": RouteConfig(backend="mqtt", channel="edge/events"),
    },
)

client = MessagingClient(cfg)
client.publish("phase_publish", {"phase": "working_stage_1"})
client.publish("board_command", {"command_code": "0x32", "message": "減速慢行"})
client.subscribe("edge_events", lambda payload: print(payload))
```

## failure_mode

- `degraded`（預設）：連線或設定失敗僅 log，服務不中斷。
- `strict`：失敗直接 raise，適合測試與早期驗證。

## 協議文件

- [MQTT 使用說明](mqtt/README.md)
- [HTTP 使用說明](http/README.md)
- [Kafka 使用說明](kafka/README.md)
- [Redis 使用說明](redis/README.md)

## 協議 Docker 快速啟動

```bash
# MQTT
docker run -d --name smart-msg-mqtt -p 1883:1883 eclipse-mosquitto:2.0

# Redis
docker run -d --name smart-msg-redis -p 6379:6379 redis:7.2-alpine

# Kafka (KRaft, single-node)
docker run -d --name smart-msg-kafka \
  -p 9092:9092 \
  -e KAFKA_ENABLE_KRAFT=yes \
  -e KAFKA_CFG_PROCESS_ROLES=broker,controller \
  -e KAFKA_CFG_NODE_ID=1 \
  -e KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER \
  -e KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \
  -e KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://127.0.0.1:9092 \
  -e KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=1@127.0.0.1:9093 \
  -e KAFKA_CFG_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
  -e KAFKA_CFG_TRANSACTION_STATE_LOG_REPLICATION_FACTOR=1 \
  -e KAFKA_CFG_TRANSACTION_STATE_LOG_MIN_ISR=1 \
  -e KAFKA_CFG_AUTO_CREATE_TOPICS_ENABLE=true \
  bitnami/kafka:latest

# HTTP (optional: publish API mock)
docker run -d --name smart-msg-httpbin -p 8080:80 kennethreitz/httpbin
```

停止：

```bash
docker rm -f smart-msg-mqtt smart-msg-redis smart-msg-kafka smart-msg-httpbin
```
