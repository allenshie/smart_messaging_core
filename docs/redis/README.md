# Redis 使用說明

## 支援能力

- publish
- subscribe

## 前置條件

- 需先啟動 Redis server
- 需安裝 `redis`

## 推薦使用方式

```python
from smart_messaging_core import MessagingClient, MessagingConfig, RedisConfig, RouteConfig

cfg = MessagingConfig(
    redis=RedisConfig(host="localhost", port=6379, db=0),
    routes={
        "phase_publish": RouteConfig(backend="redis", channel="integration:phase"),
        "edge_events": RouteConfig(backend="redis", channel="edge:events"),
    },
)

client = MessagingClient(cfg)
client.publish("phase_publish", {"phase": "working_stage_1"})
client.subscribe("edge_events", lambda payload: print(payload))
```

## 主要參數

### `RedisConfig`

- `host`
  - 範例值：`"localhost"`
  - Redis host
- `port`
  - 範例值：`6379`
  - Redis port
- `db`
  - 範例值：`0`
  - Redis database index
- `username` / `password`
  - Redis 驗證資訊，可選

### `RouteConfig`

- `backend`
  - 範例值：`"redis"`
- `channel`
  - 範例值：`"integration:phase"`
  - Redis pub/sub channel 名稱

## 測試腳本

```bash
source .venv/bin/activate
python scripts/test_redis_pubsub.py
```

## Docker image 版本參考

- image：`redis:7.2-alpine`

啟動指令：

```bash
docker run -d --name smart-msg-redis -p 6379:6379 redis:7.2-alpine
```
