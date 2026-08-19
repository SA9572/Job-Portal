from dataclasses import dataclass


@dataclass
class RetryPolicy:
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 10.0

    def get_delay(self, attempt: int) -> float:
        delay = self.base_delay * (2 ** attempt)

        return min(
            delay,
            self.max_delay,
        )