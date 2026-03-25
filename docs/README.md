# 通訊介面

`smart_messaging_core` 提供統一的 `MessagingClient`，由 route 設定選擇實際協議與 channel。

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
