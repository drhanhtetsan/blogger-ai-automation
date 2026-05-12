from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from .models import TopicRecord


FIELDNAMES = [
    "topic",
    "status",
    "title",
    "content_html",
    "tags",
    "meta_description",
    "post_url",
    "slug",
    "post_id",
    "featured_image_url",
    "publish_at",
    "last_error",
    "attempts",
    "updated_at",
]


class CSVStateStore:
    def __init__(self, csv_path: str) -> None:
        self.path = Path(csv_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            with self.path.open("w", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
                writer.writeheader()

    def load(self) -> list[TopicRecord]:
        with self.path.open("r", newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            rows = [TopicRecord.from_dict(row) for row in reader]
        return rows

    def save(self, rows: list[TopicRecord]) -> None:
        with self.path.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
            writer.writeheader()
            for row in rows:
                row.updated_at = datetime.now(timezone.utc).isoformat()
                writer.writerow(row.to_dict())

    @staticmethod
    def pending(rows: list[TopicRecord], limit: int) -> list[TopicRecord]:
        pending_rows: list[TopicRecord] = []
        for row in rows:
            normalized = row.status.strip().lower()
            if normalized in {"", "generate", "error"} and row.topic.strip():
                pending_rows.append(row)
            if len(pending_rows) >= limit:
                break
        return pending_rows
