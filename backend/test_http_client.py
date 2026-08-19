import httpx

from app.services.http_client import ResilientHttpClient
from app.services.retry_policy import RetryPolicy


class FakeTransport(httpx.BaseTransport):

    def __init__(self):
        self.calls = 0

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.calls += 1

        if self.calls < 3:
            return httpx.Response(
                status_code=503,
                request=request,
            )

        return httpx.Response(
            status_code=200,
            json={"message": "success"},
            request=request,
        )


transport = FakeTransport()

policy = RetryPolicy(
    max_attempts=3,
    base_delay=0,
    max_delay=0,
)

client = ResilientHttpClient(
    retry_policy=policy,
)

original_get = httpx.get


def fake_get(
    url,
    params=None,
    timeout=None,
):
    with httpx.Client(
        transport=transport,
        timeout=timeout,
    ) as http_client:

        return http_client.get(
            url,
            params=params,
        )


httpx.get = fake_get

try:

    print("========== HTTP RETRY TEST ==========")

    response = client.get(
        "https://example.com/test"
    )

    print("Final status:", response.status_code)
    print("Total attempts:", transport.calls)
    print("Response:", response.json())

finally:
    httpx.get = original_get