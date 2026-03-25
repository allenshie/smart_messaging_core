from smart_messaging_core import KafkaClient, KafkaConfig


def main() -> None:
    client = KafkaClient(KafkaConfig(bootstrap_servers="localhost:9092", group_id="smart-messaging-core-demo"))
    ok = client.publish("smart.messaging.demo", {"message": "hello kafka"})
    print(f"Kafka publish returned: {ok}")


if __name__ == "__main__":
    main()
