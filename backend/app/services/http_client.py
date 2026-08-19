import time

import httpx

from app.services.retry_policy import RetryPolicy


class HttpRequestError(Exception):

    def __init__(
        self,
        message: str,
        attempts: int,
        status_code: int | None = None,
        original_exception: Exception | None = None,
    ):
        super().__init__(message)

        self.attempts = attempts
        self.status_code = status_code
        self.original_exception = original_exception


class ResilientHttpClient:

    RETRYABLE_STATUS_CODES = {
        429,
        500,
        502,
        503,
        504,
    }

    def __init__(
        self,
        retry_policy: RetryPolicy | None = None,
        timeout: float = 20.0,
    ):
        self.retry_policy = retry_policy or RetryPolicy()
        self.timeout = timeout

    def get(
        self,
        url: str,
        params: dict | None = None,
    ) -> httpx.Response:

        last_exception: Exception | None = None
        last_status_code: int | None = None

        for attempt in range(
            self.retry_policy.max_attempts
        ):

            try:

                response = httpx.get(
                    url,
                    params=params,
                    timeout=self.timeout,
                )

                if (
                    response.status_code
                    not in self.RETRYABLE_STATUS_CODES
                ):
                    response.raise_for_status()
                    return response

                last_status_code = response.status_code

                last_exception = httpx.HTTPStatusError(
                    f"Retryable HTTP status: "
                    f"{response.status_code}",
                    request=response.request,
                    response=response,
                )

                delay = self._get_retry_delay(
                    response=response,
                    attempt=attempt,
                )

            except (
                httpx.TimeoutException,
                httpx.ConnectError,
                httpx.NetworkError,
            ) as exc:

                last_exception = exc
                last_status_code = None

                delay = self.retry_policy.get_delay(
                    attempt
                )

            if (
                attempt
                == self.retry_policy.max_attempts - 1
            ):
                break

            time.sleep(delay)

        attempts = self.retry_policy.max_attempts

        if last_exception is not None:

            raise HttpRequestError(
                message=str(last_exception),
                attempts=attempts,
                status_code=last_status_code,
                original_exception=last_exception,
            ) from last_exception

        raise HttpRequestError(
            message="HTTP request failed without an exception",
            attempts=attempts,
            status_code=last_status_code,
        )

    def _get_retry_delay(
        self,
        response: httpx.Response,
        attempt: int,
    ) -> float:

        if response.status_code == 429:

            retry_after = response.headers.get(
                "Retry-After"
            )

            if retry_after is not None:

                try:

                    retry_after_seconds = float(
                        retry_after
                    )

                    if retry_after_seconds >= 0:

                        return min(
                            retry_after_seconds,
                            self.retry_policy.max_delay,
                        )

                except ValueError:
                    pass

        return self.retry_policy.get_delay(
            attempt
        )