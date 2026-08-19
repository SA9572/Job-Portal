import httpx

from app.services.http_client import ResilientHttpClient
from app.services.retry_policy import RetryPolicy


policy = RetryPolicy(
    max_attempts=3,
    base_delay=1,
    max_delay=10,
)

client = ResilientHttpClient(
    retry_policy=policy
)


print("========== RETRY-AFTER TEST ==========")


response = httpx.Response(
    status_code=429,
    headers={
        "Retry-After": "5"
    },
)


delay = client._get_retry_delay(
    response=response,
    attempt=0,
)


print("HTTP status:", response.status_code)
print("Retry-After:", response.headers["Retry-After"])
print("Calculated delay:", delay)


print("\n========== EXPECTED ==========")

print("Expected delay: 5.0")