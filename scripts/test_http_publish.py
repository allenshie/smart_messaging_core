from smart_messaging_core import HttpClient, HttpConfig


def main() -> None:
    client = HttpClient(HttpConfig(base_url="http://localhost:8080"))
    ok = client.publish("/health", {"message": "hello http"})
    print(f"HTTP publish returned: {ok}")


if __name__ == "__main__":
    main()
