from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


TRUE_VALUES = {"1", "true", "yes", "y", "on"}


@dataclass
class Settings:
    environment: str
    gemini_api_key: str
    pexels_api_key: str
    wordpress_url: str
    wordpress_username: str
    wordpress_app_password: str
    wordpress_default_categories: str
    wordpress_post_status: str
    tracking_csv_path: str
    comments_csv_path: str
    batch_size: int
    max_retries: int
    request_timeout: int
    dry_run: bool
    slack_webhook_url: str
    user_agent: str

    def validate(self) -> None:
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required")
        if not self.wordpress_post_status:
            raise ValueError("WORDPRESS_POST_STATUS is required")
        if self.wordpress_post_status not in {"draft", "publish", "future"}:
            raise ValueError("WORDPRESS_POST_STATUS must be one of: draft, publish, future")
        if not self.dry_run:
            required = {
                "WORDPRESS_URL": self.wordpress_url,
                "WORDPRESS_USERNAME": self.wordpress_username,
                "WORDPRESS_APP_PASSWORD": self.wordpress_app_password,
            }
            missing = [k for k, v in required.items() if not v]
            if missing:
                raise ValueError("Missing required WordPress settings: " + ", ".join(missing))


def load_env_file(path: str) -> None:
    env_file = Path(path)
    if not env_file.exists():
        return
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _to_bool(value: str, default: bool) -> bool:
    if not value:
        return default
    return value.strip().lower() in TRUE_VALUES


def load_settings(environment: str = "dev") -> Settings:
    repo_root = Path(__file__).resolve().parents[2]
    load_env_file(str(repo_root / ".env"))
    load_env_file(str(repo_root / "config" / "environments" / f"{environment}.env"))

    settings = Settings(
        environment=environment,
        gemini_api_key=os.environ.get("GEMINI_API_KEY", ""),
        pexels_api_key=os.environ.get("PEXELS_API_KEY", ""),
        wordpress_url=os.environ.get("WORDPRESS_URL", "").rstrip("/"),
        wordpress_username=os.environ.get("WORDPRESS_USERNAME", ""),
        wordpress_app_password=os.environ.get("WORDPRESS_APP_PASSWORD", ""),
        wordpress_default_categories=os.environ.get("WORDPRESS_DEFAULT_CATEGORIES", "Automation"),
        wordpress_post_status=os.environ.get("WORDPRESS_POST_STATUS", "draft").lower(),
        tracking_csv_path=os.environ.get("TRACKING_CSV_PATH", str(repo_root / "config" / "topics.csv")),
        comments_csv_path=os.environ.get("COMMENTS_CSV_PATH", str(repo_root / "config" / "comments.csv")),
        batch_size=int(os.environ.get("BATCH_SIZE", "3")),
        max_retries=int(os.environ.get("MAX_RETRIES", "3")),
        request_timeout=int(os.environ.get("REQUEST_TIMEOUT", "30")),
        dry_run=_to_bool(os.environ.get("DRY_RUN", "true"), True),
        slack_webhook_url=os.environ.get("SLACK_WEBHOOK_URL", ""),
        user_agent=os.environ.get("USER_AGENT", "wordpress-ai-automation/1.0"),
    )
    settings.validate()
    return settings
