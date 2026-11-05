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
- `max_queued_messages`
  - 範例值：`1000`
  - QoS 1 以上斷線時最多保留的訊息數，超過時 publish 回傳 `False`；`0` 代表不限制

### `RouteConfig`

- `backend`
  - 範例值：`"mqtt"`
- `channel`
  - 範例值：`"integration/phase"`
  - MQTT topic 名稱

## 連線行為

- 建立 `MessagingClient` 時，只要路由有用到 MQTT 就開始連線。連線與重連都在 paho 的背景執行緒進行（間隔 1 到 30 秒），不會卡住呼叫端。
- 尚未連上時，publish 立刻回傳 `False`。QoS 0 的訊息會直接丟棄，所以剛建立就馬上 publish 仍可能失敗；QoS 1 以上會排隊，上限為 `max_queued_messages`。
- 同一個 `client_id` 只能有一條連線。建立多個 `MessagingClient` 時，不要讓它們設定相同的 `client_id`，否則 broker 會讓它們互相踢線。
- 重連後會自動重新訂閱。
- `MessagingClient.is_connected(route_key)` 回傳該路由的連線狀態；backend 沒有連線狀態或路由無效時回傳 `None`。
- 連線失敗時會輸出 WARNING：連不上時包含 broker 位址，broker 拒絕時（例如帳密錯誤）包含 `rc`。

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
