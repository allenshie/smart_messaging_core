# HTTP 使用說明

## 支援能力

- publish（HTTP client -> 目標 API）
- subscribe（本地 webhook server 接收 POST）

## 設定欄位

`HttpConfig` 主要欄位：

- `base_url`：publish 目標服務 URL（例如 `http://localhost:8080`）
- `timeout_seconds`：publish timeout
- `listen_host`：subscribe webhook server listen host
- `listen_port`：subscribe webhook server listen port

## 最小設定（publish）

```python
from smart_messaging_core import HttpConfig, HttpClient

cfg = HttpConfig(base_url="http://localhost:8080")
client = HttpClient(cfg)
client.publish("/phase", {"phase": "working_stage_1"})
```

## 最小設定（subscribe）

```python
from smart_messaging_core import HttpConfig, HttpClient

cfg = HttpConfig(listen_host="0.0.0.0", listen_port=9000)
client = HttpClient(cfg)

client.subscribe("/edge/events", lambda payload: print(payload))
# 現在可接收 POST http://0.0.0.0:9000/edge/events
```

## 透過 MessagingClient 使用

```python
from smart_messaging_core import MessagingClient, MessagingConfig, HttpConfig, RouteConfig

cfg = MessagingConfig(
    http=HttpConfig(
        base_url="http://localhost:8080",
        listen_host="0.0.0.0",
        listen_port=9000,
    ),
    routes={
        "phase_publish": RouteConfig(backend="http", channel="/phase"),
        "edge_events": RouteConfig(backend="http", channel="/edge/events"),
    },
)

client = MessagingClient(cfg)
client.subscribe("edge_events", lambda payload: print(payload))
client.publish("phase_publish", {"phase": "working"})
```

## lifecycle

- subscribe 後會在背景執行本地 webhook server。
- 使用完成請呼叫 `client.close()` 釋放資源與 listen port。

## 測試腳本

```bash
source .venv/bin/activate
python scripts/test_http_publish.py  # subscribe + publish + close
```

## Docker image 版本參考

- 本機 loopback 測試：不需要額外 image（腳本會自啟 webhook server）
- 若只驗證 publish 對外 API，可選 image：`kennethreitz/httpbin`

啟動指令（可選，僅測 publish 外部 API）：

```bash
docker run -d --name smart-msg-httpbin -p 8080:80 kennethreitz/httpbin
```
