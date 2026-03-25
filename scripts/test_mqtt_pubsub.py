from smart_messaging_core import MqttClient, MqttConfig


def main() -> None:
    client = MqttClient(MqttConfig(host="localhost", port=1883, qos=1, retain=False))
    client.publish("smart-messaging-core/demo", {"message": "hello mqtt"})
    print("Published demo MQTT message to smart-messaging-core/demo")


if __name__ == "__main__":
    main()
