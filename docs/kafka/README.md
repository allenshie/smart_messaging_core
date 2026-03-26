# Kafka 使用說明

## 支援能力

- publish
- subscribe

## 前置條件

- 需先啟動 Kafka broker
- 需安裝 `kafka-python`

## 最小設定

```python
from smart_messaging_core import KafkaConfig, KafkaClient

cfg = KafkaConfig(bootstrap_servers="localhost:9092", group_id="demo-group")
client = KafkaClient(cfg)
```

## Publish

```python
client.publish("integration.phase", {"phase": "working_stage_1"})
```

## Subscribe

```python
client.subscribe("integration.phase", lambda payload: print(payload))
```

## 測試腳本

```bash
source .venv/bin/activate
python scripts/test_kafka_pubsub.py  # subscribe + publish + close
```

## Docker image 版本參考

- image：`bitnami/kafka:latest`

啟動指令：

```bash
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
```
