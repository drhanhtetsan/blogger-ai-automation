from __future__ import annotations

import re


FORBIDDEN_TAGS = [r"<script[\s>]", r"<iframe[\s>]", r"onerror=", r"onload="]


def validate_html_content(html: str) -> list[str]:
    issues: list[str] = []
    text = (html or "").strip()

    if not text:
        issues.append("HTML is empty")
        return issues
    if "<h1" not in text.lower():
        issues.append("HTML must include an <h1> heading")
    if "<p" not in text.lower():
        issues.append("HTML must include at least one <p> paragraph")
    if len(text) < 800:
        issues.append("HTML appears too short for a full blog post")

    for pattern in FORBIDDEN_TAGS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            issues.append(f"HTML contains forbidden pattern: {pattern}")

    return issues
