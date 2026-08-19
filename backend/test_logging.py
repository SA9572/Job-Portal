import os

from app.core.logging_config import LOG_FILE, logger


print("========== STRUCTURED LOGGING TEST ==========")

# =========================================
# TEST 1: EMIT LOG MESSAGES
# =========================================

print()
print("========== TEST 1: EMIT LOG MESSAGES ==========")

test_msg_info = "Testing structured logging INFO entry"
test_msg_warn = "Testing structured logging WARNING entry"

logger.info(test_msg_info)
logger.warning(test_msg_warn)

print("Log messages emitted to logger.")

# =========================================
# TEST 2: VERIFY LOG FILE CREATION & FORMAT
# =========================================

print()
print("========== TEST 2: VERIFY LOG FILE ==========")

print("Log file path:", LOG_FILE)

assert os.path.exists(LOG_FILE), f"Log file missing: {LOG_FILE}"
assert os.path.getsize(LOG_FILE) > 0, "Log file is empty"

with open(LOG_FILE, "r", encoding="utf-8") as f:
    content = f.read()

assert test_msg_info in content, f"Missing test message: {test_msg_info}"
assert test_msg_warn in content, f"Missing test message: {test_msg_warn}"

print("Log file content verified successfully.")

print()
print("========== STRUCTURED LOGGING TEST COMPLETED ==========")
