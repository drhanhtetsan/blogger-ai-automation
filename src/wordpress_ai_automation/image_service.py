from __future__ import annotations

import json
import logging
from urllib import parse, request

from .models import ImageResult


LOGGER = logging.getLogger(__name__)


class ImageService:
    def __init__(self, api_key: str, timeout: int, user_agent: str) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self.user_agent = user_agent

    def find_image(self, query: str) -> ImageResult | None:
        if not self.api_key:
            LOGGER.warning("PEXELS_API_KEY not set; skipping featured image")
            return None

        cleaned_query = query.split(":", 1)[0].split("-", 1)[0].strip()
        url = (
            "https://api.pexels.com/v1/search?"
            + parse.urlencode({"query": cleaned_query, "per_page": 1, "orientation": "landscape"})
        )
        req = request.Request(
            url=url,
            headers={"Authorization": self.api_key, "User-Agent": self.user_agent},
            method="GET",
        )
        with request.urlopen(req, timeout=self.timeout) as response:  # noqa: S310
            payload = json.loads(response.read().decode("utf-8"))
        photos = payload.get("photos") or []
        if not photos:
            LOGGER.info("No image found for query '%s'", cleaned_query)
            return None

        photo = photos[0]
        return ImageResult(
            image_url=photo.get("src", {}).get("large", ""),
            photographer=photo.get("photographer", ""),
            photographer_url=photo.get("photographer_url", ""),
            source_url=photo.get("url", ""),
        )
