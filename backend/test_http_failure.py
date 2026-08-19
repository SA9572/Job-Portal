import httpx

from app.services.http_client import (
    HttpRequestError,
    ResilientHttpClient,
)
from app.services.retry_policy import RetryPolicy


class FakeFailureTransport(httpx.BaseTransport):

    def __init__(self):
        self.calls = 0

    def handle_request(
        self,
        request: httpx.Request,
    ) -> httpx.Response:

        self.calls += 1

        return httpx.Response(
            status_code=503,
            request=request,
        )


transport = FakeFailureTransport()

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

    print("========== EXHAUSTED RETRY TEST ==========")

    try:

        client.get(
            "https://example.com/test"
        )

    except HttpRequestError as exc:

        print("Error type:", type(exc).__name__)
        print("Attempts:", exc.attempts)
        print("Status code:", exc.status_code)
        print("Total transport calls:", transport.calls)
        print("Message:", exc)


finally:

    httpx.get = original_get