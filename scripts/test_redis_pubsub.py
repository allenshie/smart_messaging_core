from smart_messaging_core import RedisClient, RedisConfig


def main() -> None:
    client = RedisClient(RedisConfig(host="localhost", port=6379, db=0))
    ok = client.publish("smart-messaging-core:demo", {"message": "hello redis"})
    print(f"Redis publish returned: {ok}")


if __name__ == "__main__":
    main()
