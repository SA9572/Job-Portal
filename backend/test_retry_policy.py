from app.services.retry_policy import RetryPolicy


policy = RetryPolicy()

print("========== RETRY POLICY ==========")

print("Maximum attempts:", policy.max_attempts)
print("Base delay:", policy.base_delay)
print("Maximum delay:", policy.max_delay)

print("\n========== BACKOFF DELAYS ==========")

for attempt in range(5):
    delay = policy.get_delay(attempt)
    print(f"Attempt {attempt}: {delay} seconds")