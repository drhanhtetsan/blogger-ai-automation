from __future__ import annotations

import json
import logging
from urllib import request

from .models import GeneratedPost


LOGGER = logging.getLogger(__name__)
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"


class AIService:
    def __init__(self, api_key: str, timeout: int, user_agent: str) -> None:
        self.api_key = api_key
        self.timeout = timeout
        self.user_agent = user_agent

    def _call_gemini(self, prompt: str) -> str:
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7},
        }
        req = request.Request(
            url=f"{GEMINI_ENDPOINT}?key={self.api_key}",
            method="POST",
            headers={"Content-Type": "application/json", "User-Agent": self.user_agent},
            data=json.dumps(payload).encode("utf-8"),
        )
        with request.urlopen(req, timeout=self.timeout) as response:  # noqa: S310
            data = json.loads(response.read().decode("utf-8"))
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()

    @staticmethod
    def _extract_json(raw: str) -> dict:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            start, end = raw.find("{"), raw.rfind("}")
            if start >= 0 and end > start:
                return json.loads(raw[start : end + 1])
            raise

    def generate_post(self, topic: str) -> GeneratedPost:
        prompt = (
            "You are an SEO blog generator. Return strict JSON with keys: title, html, tags, meta_description. "
            "Rules: html must start with <h1>, include multiple <h2> and <p> sections, and be 500-700 words. "
            "tags must be an array of 3-7 concise tags. Topic: "
            f"{topic}"
        )
        raw = self._call_gemini(prompt)
        parsed = self._extract_json(raw)
        tags = parsed.get("tags") or []
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(",") if t.strip()]

        post = GeneratedPost(
            title=(parsed.get("title") or topic).strip(),
            html=(parsed.get("html") or "").strip(),
            tags=tags,
            meta_description=(parsed.get("meta_description") or "").strip(),
        )
        LOGGER.info("Generated post draft for topic '%s'", topic)
        return post

    def generate_alt_text(self, title: str) -> str:
        prompt = (
            "Create one concise image alt text under 125 characters. "
            "Return plain text only for topic/title: "
            f"{title}"
        )
        alt_text = self._call_gemini(prompt)
        return alt_text.replace('"', "").strip().rstrip(".")
