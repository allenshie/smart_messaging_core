# smart_messaging_core

可擴充的通訊核心套件，提供統一的 `MessagingClient` facade，並可依 route 將訊息導向不同協議。

## PyPI 發佈狀態

- 正式 PyPI：`smart-messaging-core==0.1.1`
- 套件頁面：<https://pypi.org/project/smart-messaging-core/>

安裝：

```bash
pip install smart-messaging-core==0.1.1
```

## 本機開發

```bash
git clone https://github.com/allenshie/smart_messaging_core.git
cd smart_messaging_core
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 目前支援的協議

- `mqtt`: publish / subscribe
- `http`: publish / subscribe（webhook）
- `kafka`: publish / subscribe
- `redis`: publish / subscribe

## 推薦使用方式

對外建議統一使用 `MessagingClient`，由 `routes` 決定實際協議與目標位置。

```python
from smart_messaging_core import (
    HttpConfig,
    MessagingClient,
    MessagingConfig,
    MqttConfig,
    RouteConfig,
)

cfg = MessagingConfig(
    mqtt=MqttConfig(host="localhost", port=1883, qos=1, retain=True),
    http=HttpConfig(base_url="http://localhost:8080"),
    routes={
        "phase_publish": RouteConfig(backend="http", channel="/phase"),
        "edge_events": RouteConfig(backend="mqtt", channel="edge/events"),
    },
)

client = MessagingClient(cfg)
client.publish("phase_publish", {"phase": "working_stage_1"})
client.subscribe("edge_events", lambda payload: print(payload))
```

## 文件

- [通訊介面與使用範例](docs/README.md)
- [MQTT 使用說明](docs/mqtt/README.md)
- [HTTP 使用說明](docs/http/README.md)
- [Kafka 使用說明](docs/kafka/README.md)
- [Redis 使用說明](docs/redis/README.md)

## 設計說明

- 對外 API：`MessagingClient`
- 協議實作集中在 `protocols/`
- 每個協議提供對應 `Config` 與 `Client`
- route-based 設計可讓不同用途走不同 backend/channel
- 錯誤處理可透過 `failure_mode` 控制（`degraded` 只 log；`strict` 會 raise）
