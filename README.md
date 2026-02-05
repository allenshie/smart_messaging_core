# smart_messaging_core

最小可用的通訊模組，供 edge / integration 端共用。

## 安裝（本機）

```bash
cd /home/allen/Documents/project/asia-bay/SmartWarehousing/test/smart_messaging_core
pip install -e .
```

## 文件

- [通訊介面與使用範例](docs/README.md)
- [MQTT 使用範例](docs/mqtt/README.md)

## 設計說明

- 核心 API：`MessagingClient`
- 協議實作集中在 `protocols/`（目前支援 MQTT、HTTP）
- 錯誤處理可透過 `failure_mode` 控制（`degraded` 只 log；`strict` 會 raise）
