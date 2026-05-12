from __future__ import annotations

import base64
from datetime import datetime, timezone
import json
import re
from urllib import parse, request


class WordPressClient:
    def __init__(
        self,
        base_url: str,
        username: str,
        app_password: str,
        timeout: int,
        user_agent: str,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.user_agent = user_agent
        credentials = f"{username}:{app_password}".encode("utf-8")
        self.authorization = "Basic " + base64.b64encode(credentials).decode("utf-8")

    @staticmethod
    def slugify(value: str) -> str:
        value = re.sub(r"<[^>]*>", "", value)
        value = re.sub(r"[^a-zA-Z0-9\\s-]", "", value).strip().lower()
        value = re.sub(r"[\\s_-]+", "-", value)
        return value or "post"

    def _request(self, method: str, path: str, payload: dict | None = None, headers: dict | None = None) -> dict | list:
        merged_headers = {
            "Authorization": self.authorization,
            "User-Agent": self.user_agent,
        }
        if headers:
            merged_headers.update(headers)

        data = None
        if payload is not None:
            merged_headers["Content-Type"] = "application/json"
            data = json.dumps(payload).encode("utf-8")

        req = request.Request(
            url=f"{self.base_url}{path}",
            method=method,
            headers=merged_headers,
            data=data,
        )
        with request.urlopen(req, timeout=self.timeout) as response:  # noqa: S310
            body = response.read().decode("utf-8")
        if not body:
            return {}
        return json.loads(body)

    def ensure_tag_ids(self, tag_names: list[str]) -> list[int]:
        ids: list[int] = []
        for tag_name in tag_names:
            encoded = parse.quote(tag_name)
            existing = self._request("GET", f"/wp-json/wp/v2/tags?search={encoded}&per_page=100")
            exact = next((tag for tag in existing if tag.get("name", "").lower() == tag_name.lower()), None)
            if exact:
                ids.append(int(exact["id"]))
                continue
            created = self._request("POST", "/wp-json/wp/v2/tags", payload={"name": tag_name})
            ids.append(int(created["id"]))
        return ids

    def ensure_category_ids(self, category_names: list[str]) -> list[int]:
        ids: list[int] = []
        for category_name in category_names:
            encoded = parse.quote(category_name)
            existing = self._request("GET", f"/wp-json/wp/v2/categories?search={encoded}&per_page=100")
            exact = next((cat for cat in existing if cat.get("name", "").lower() == category_name.lower()), None)
            if exact:
                ids.append(int(exact["id"]))
                continue
            created = self._request("POST", "/wp-json/wp/v2/categories", payload={"name": category_name})
            ids.append(int(created["id"]))
        return ids

    def post_exists_by_slug(self, slug: str) -> bool:
        found = self._request("GET", f"/wp-json/wp/v2/posts?slug={parse.quote(slug)}")
        return bool(found)

    def post_exists_by_title(self, title: str) -> bool:
        found = self._request("GET", f"/wp-json/wp/v2/posts?search={parse.quote(title)}&per_page=20")
        for post in found:
            rendered = (post.get("title") or {}).get("rendered", "")
            if rendered.strip().lower() == title.strip().lower():
                return True
        return False

    def next_unique_slug(self, preferred_slug: str) -> str:
        if not self.post_exists_by_slug(preferred_slug):
            return preferred_slug
        suffix = datetime.now(timezone.utc).strftime("%Y%m%d")
        candidate = f"{preferred_slug}-{suffix}"
        index = 2
        while self.post_exists_by_slug(candidate):
            candidate = f"{preferred_slug}-{suffix}-{index}"
            index += 1
        return candidate

    def upload_media_from_url(self, image_url: str, alt_text: str, title: str, caption: str = "") -> tuple[int, str]:
        image_req = request.Request(image_url, method="GET", headers={"User-Agent": self.user_agent})
        with request.urlopen(image_req, timeout=self.timeout) as response:  # noqa: S310
            body = response.read()
            content_type = response.headers.get("Content-Type", "image/jpeg")

        slug = self.slugify(title)
        headers = {
            "Authorization": self.authorization,
            "User-Agent": self.user_agent,
            "Content-Type": content_type,
            "Content-Disposition": f'attachment; filename="{slug}.jpg"',
        }
        upload_req = request.Request(
            url=f"{self.base_url}/wp-json/wp/v2/media",
            method="POST",
            headers=headers,
            data=body,
        )
        with request.urlopen(upload_req, timeout=self.timeout) as response:  # noqa: S310
            media = json.loads(response.read().decode("utf-8"))

        media_id = int(media["id"])
        self._request(
            "POST",
            f"/wp-json/wp/v2/media/{media_id}",
            payload={"alt_text": alt_text, "caption": caption},
        )
        return media_id, media.get("source_url", "")

    def create_post(
        self,
        title: str,
        content_html: str,
        slug: str,
        tag_ids: list[int],
        category_ids: list[int],
        status: str,
        featured_media_id: int | None,
        excerpt: str,
        publish_at: str,
    ) -> dict:
        payload = {
            "title": title,
            "content": content_html,
            "slug": slug,
            "status": status,
            "tags": tag_ids,
            "categories": category_ids,
            "featured_media": featured_media_id or 0,
            "excerpt": excerpt,
        }
        if status == "future" and publish_at:
            payload["date"] = publish_at
        return self._request("POST", "/wp-json/wp/v2/posts", payload=payload)

    def sync_comments(self, per_page: int = 100) -> list[dict]:
        all_comments: list[dict] = []
        page = 1
        while True:
            result = self._request("GET", f"/wp-json/wp/v2/comments?per_page={per_page}&page={page}")
            if not result:
                break
            all_comments.extend(result)
            if len(result) < per_page:
                break
            page += 1
        return all_comments
