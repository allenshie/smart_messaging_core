# Redis 使用說明

## 支援能力

- publish
- subscribe

## 前置條件

- 需先啟動 Redis server
- 需安裝 `redis`

## 最小設定

```python
from smart_messaging_core import RedisConfig, RedisClient

cfg = RedisConfig(host="localhost", port=6379, db=0)
client = RedisClient(cfg)
```

## Publish

```python
client.publish("integration:phase", {"phase": "working_stage_1"})
```

## Subscribe

```python
client.subscribe("integration:phase", lambda payload: print(payload))
```

## 測試腳本

```bash
source .venv/bin/activate
python scripts/test_redis_pubsub.py  # subscribe + publish + close
```

## Docker image 版本參考

- image：`redis:7.2-alpine`

啟動指令：

```bash
docker run -d --name smart-msg-redis -p 6379:6379 redis:7.2-alpine
```
