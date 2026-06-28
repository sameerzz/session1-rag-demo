from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import requests


TARGET_URL = "http://35.232.150.97:8000/chat"
TOTAL_REQUESTS = 100
MAX_WORKERS = 100
TIMEOUT_SECONDS = 15


def send_request(request_number: int) -> dict[str, Any]:
    # Uses the VM public IP because students run this from their laptops, outside the cloud host.
    response = requests.post(
        TARGET_URL,
        json={"message": f"load-test-request-{request_number}"},
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    successes = 0
    failures = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(send_request, i) for i in range(1, TOTAL_REQUESTS + 1)]

        for future in as_completed(futures):
            try:
                future.result()
                successes += 1
            except Exception as exc:
                failures += 1
                print(f"request failed: {exc}")

    print(f"completed={TOTAL_REQUESTS} successes={successes} failures={failures}")


if __name__ == "__main__":
    main()
