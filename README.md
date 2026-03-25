# smart_messaging_core

可擴充的通訊核心套件，提供統一的 `MessagingClient` facade，並可依 route 將訊息導向不同協議。

## 目前支援的協議

- `mqtt`: publish / subscribe
- `http`: publish / subscribe（webhook）
- `kafka`: publish / subscribe
- `redis`: publish / subscribe

註：`kafka` 與 `redis` 目前已提供 client/config 與文件、測試腳本骨架；若要實際連線驗證，需安裝對應套件並啟動外部服務。

## 安裝（本機）

```bash
cd /home/allen/Documents/project/asia-bay/SmartWarehousing/test/smart_messaging_core
pip install -e .
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
