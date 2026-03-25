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
python scripts/test_kafka_pubsub.py
```
