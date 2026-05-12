from __future__ import annotations

import json
from urllib import request


def send_slack_alert(webhook_url: str, message: str, timeout: int, user_agent: str) -> None:
    if not webhook_url:
        return
    payload = {"text": message}
    req = request.Request(
        url=webhook_url,
        method="POST",
        headers={"Content-Type": "application/json", "User-Agent": user_agent},
        data=json.dumps(payload).encode("utf-8"),
    )
    with request.urlopen(req, timeout=timeout):  # noqa: S310
        return
