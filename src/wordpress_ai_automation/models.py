from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class GeneratedPost:
    title: str
    html: str
    tags: list[str]
    meta_description: str


@dataclass
class ImageResult:
    image_url: str
    photographer: str = ""
    photographer_url: str = ""
    source_url: str = ""


@dataclass
class TopicRecord:
    topic: str
    status: str = "Generate"
    title: str = ""
    content_html: str = ""
    tags: str = ""
    meta_description: str = ""
    post_url: str = ""
    slug: str = ""
    post_id: str = ""
    featured_image_url: str = ""
    publish_at: str = ""
    last_error: str = ""
    attempts: int = 0
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @staticmethod
    def from_dict(data: dict[str, str]) -> "TopicRecord":
        return TopicRecord(
            topic=(data.get("topic") or "").strip(),
            status=(data.get("status") or "").strip() or "Generate",
            title=(data.get("title") or "").strip(),
            content_html=data.get("content_html") or "",
            tags=(data.get("tags") or "").strip(),
            meta_description=(data.get("meta_description") or "").strip(),
            post_url=(data.get("post_url") or "").strip(),
            slug=(data.get("slug") or "").strip(),
            post_id=(data.get("post_id") or "").strip(),
            featured_image_url=(data.get("featured_image_url") or "").strip(),
            publish_at=(data.get("publish_at") or "").strip(),
            last_error=(data.get("last_error") or "").strip(),
            attempts=int((data.get("attempts") or "0").strip() or "0"),
            updated_at=(data.get("updated_at") or "").strip() or datetime.now(timezone.utc).isoformat(),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "topic": self.topic,
            "status": self.status,
            "title": self.title,
            "content_html": self.content_html,
            "tags": self.tags,
            "meta_description": self.meta_description,
            "post_url": self.post_url,
            "slug": self.slug,
            "post_id": self.post_id,
            "featured_image_url": self.featured_image_url,
            "publish_at": self.publish_at,
            "last_error": self.last_error,
            "attempts": str(self.attempts),
            "updated_at": self.updated_at,
        }
