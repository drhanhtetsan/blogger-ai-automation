from __future__ import annotations

import time
from urllib.error import HTTPError


RETRYABLE_HTTP_CODES = {408, 425, 429, 500, 502, 503, 504}


def with_retries(func, max_retries: int, base_delay_seconds: float = 1.5):
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            return func()
        except HTTPError as error:
            last_error = error
            if error.code not in RETRYABLE_HTTP_CODES or attempt == max_retries:
                raise
        except Exception as error:  # noqa: BLE001
            last_error = error
            if attempt == max_retries:
                raise
        sleep_seconds = base_delay_seconds * (2 ** (attempt - 1))
        time.sleep(sleep_seconds)
    if last_error:
        raise last_error
    raise RuntimeError("Retry operation failed without explicit error")
