# 通訊介面

`smart_messaging_core` 提供統一的 `MessagingClient`，由設定選擇實際協議。

## 使用範例

```python
from smart_messaging_core import MessagingClient, MessagingConfig, MqttConfig

cfg = MessagingConfig(
    publish_backend="mqtt",
    subscribe_backend="mqtt",
    mqtt=MqttConfig(
        host="localhost",
        port=1883,
        qos=1,
        retain=True,
        # auth_enabled=True, username="mqtt_user", password="mqtt_password",
    ),
)

client = MessagingClient(cfg)
client.publish("integration/phase", {"phase": "working_stage_1"})
client.subscribe("integration/phase", lambda payload: print(payload))
```

## failure_mode

- `degraded`（預設）：連線失敗僅 log，服務不會中斷。
- `strict`：連線失敗會 raise 例外，適合測試環境。

## 協議文件

- [MQTT 使用範例](mqtt/README.md)
