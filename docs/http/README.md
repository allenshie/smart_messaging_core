# HTTP 使用說明

## 支援能力

- publish（HTTP client -> 目標 API）
- subscribe（本地 webhook server 接收 POST）

## 推薦使用方式

```python
from smart_messaging_core import HttpConfig, MessagingClient, MessagingConfig, RouteConfig

cfg = MessagingConfig(
    http=HttpConfig(
        base_url="http://localhost:8080",
        listen_host="0.0.0.0",
        listen_port=9000,
        timeout_seconds=5,
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

## 主要參數

### `HttpConfig`

- `base_url`
  - 範例值：`"http://localhost:8080"`
  - publish 目標服務 URL
- `timeout_seconds`
  - 範例值：`5`
  - publish timeout 秒數
- `listen_host`
  - 範例值：`"0.0.0.0"`
  - subscribe webhook server listen host
- `listen_port`
  - 範例值：`9000`
  - subscribe webhook server listen port

### `RouteConfig`

- `backend`
  - 範例值：`"http"`
- `channel`
  - 範例值：`"/phase"`
  - HTTP path，建議以 `/` 開頭

## lifecycle

- `subscribe()` 後會在背景啟動本地 webhook server。
- 使用完成請呼叫 `client.close()` 釋放資源與 listen port。

## 測試腳本

```bash
source .venv/bin/activate
python scripts/test_http_publish.py
```

## Docker image 版本參考

- 本機 loopback 測試：不需要額外 image（腳本會自啟 webhook server）
- 若只驗證 publish 對外 API，可選 image：`kennethreitz/httpbin`

啟動指令（可選，僅測 publish 外部 API）：

```bash
docker run -d --name smart-msg-httpbin -p 8080:80 kennethreitz/httpbin
```
