from __future__ import annotations

import csv
from datetime import datetime, timezone
import logging
from pathlib import Path

from .ai_service import AIService
from .alerts import send_slack_alert
from .config import Settings
from .image_service import ImageService
from .retry import with_retries
from .state_store import CSVStateStore
from .validators import validate_html_content
from .wordpress_client import WordPressClient


LOGGER = logging.getLogger(__name__)


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def _format_error(error: Exception) -> str:
    message = str(error).strip()
    return message[:700] if message else error.__class__.__name__


def run_batch(settings: Settings) -> dict[str, int]:
    configure_logging()

    store = CSVStateStore(settings.tracking_csv_path)
    all_rows = store.load()
    pending_rows = store.pending(all_rows, settings.batch_size)

    ai_service = AIService(settings.gemini_api_key, settings.request_timeout, settings.user_agent)
    image_service = ImageService(settings.pexels_api_key, settings.request_timeout, settings.user_agent)

    wp_client = None
    if not settings.dry_run:
        wp_client = WordPressClient(
            base_url=settings.wordpress_url,
            username=settings.wordpress_username,
            app_password=settings.wordpress_app_password,
            timeout=settings.request_timeout,
            user_agent=settings.user_agent,
        )

    generated = published = errored = 0

    for row in pending_rows:
        row.attempts += 1
        try:
            generated_post = with_retries(
                lambda: ai_service.generate_post(row.topic),
                max_retries=settings.max_retries,
            )
            issues = validate_html_content(generated_post.html)
            if issues:
                raise ValueError("; ".join(issues))

            image = with_retries(
                lambda: image_service.find_image(generated_post.title),
                max_retries=settings.max_retries,
            )
            alt_text = ""
            if image:
                alt_text = with_retries(
                    lambda: ai_service.generate_alt_text(generated_post.title),
                    max_retries=settings.max_retries,
                )

            row.title = generated_post.title
            row.content_html = generated_post.html
            row.tags = ", ".join(generated_post.tags)
            row.meta_description = generated_post.meta_description
            row.featured_image_url = image.image_url if image else ""
            row.updated_at = datetime.now(timezone.utc).isoformat()

            if settings.dry_run:
                row.status = "Draft"
                row.last_error = ""
                generated += 1
                continue

            assert wp_client is not None
            base_slug = row.slug or wp_client.slugify(row.title)
            unique_slug = wp_client.next_unique_slug(base_slug)

            final_title = row.title
            if wp_client.post_exists_by_title(final_title):
                final_title = f"{final_title} ({datetime.now(timezone.utc).strftime('%Y-%m-%d')})"

            tag_ids = wp_client.ensure_tag_ids(generated_post.tags)
            category_names = [name.strip() for name in settings.wordpress_default_categories.split(",") if name.strip()]
            category_ids = wp_client.ensure_category_ids(category_names)

            media_id = None
            featured_image_url = row.featured_image_url
            if image and image.image_url:
                caption = ""
                if image.photographer:
                    caption = f"Photo by {image.photographer}"
                media_id, featured_image_url = wp_client.upload_media_from_url(
                    image_url=image.image_url,
                    alt_text=alt_text or final_title,
                    title=final_title,
                    caption=caption,
                )

            post = wp_client.create_post(
                title=final_title,
                content_html=row.content_html,
                slug=unique_slug,
                tag_ids=tag_ids,
                category_ids=category_ids,
                status=settings.wordpress_post_status,
                featured_media_id=media_id,
                excerpt=row.meta_description,
                publish_at=row.publish_at,
            )

            row.status = "Published"
            row.slug = unique_slug
            row.post_id = str(post.get("id", ""))
            row.post_url = post.get("link", "")
            row.featured_image_url = featured_image_url
            row.last_error = ""
            published += 1
        except Exception as error:  # noqa: BLE001
            row.status = "Error"
            row.last_error = _format_error(error)
            errored += 1
            LOGGER.exception("Failed processing topic '%s'", row.topic)

    store.save(all_rows)

    summary = {"processed": len(pending_rows), "generated": generated, "published": published, "errored": errored}
    LOGGER.info("Run summary: %s", summary)

    if errored:
        send_slack_alert(
            webhook_url=settings.slack_webhook_url,
            message=f"WordPress automation finished with {errored} error(s): {summary}",
            timeout=settings.request_timeout,
            user_agent=settings.user_agent,
        )

    return summary


def sync_comments(settings: Settings) -> int:
    configure_logging()
    if settings.dry_run:
        raise ValueError("Set DRY_RUN=false to sync comments from WordPress")

    wp_client = WordPressClient(
        base_url=settings.wordpress_url,
        username=settings.wordpress_username,
        app_password=settings.wordpress_app_password,
        timeout=settings.request_timeout,
        user_agent=settings.user_agent,
    )
    comments = wp_client.sync_comments()

    path = Path(settings.comments_csv_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as fh:
        fieldnames = ["id", "post", "author", "date", "status", "content"]
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for item in comments:
            writer.writerow(
                {
                    "id": item.get("id", ""),
                    "post": item.get("post", ""),
                    "author": (item.get("author_name") or "").strip(),
                    "date": item.get("date", ""),
                    "status": item.get("status", ""),
                    "content": (item.get("content") or {}).get("rendered", ""),
                }
            )

    LOGGER.info("Synced %s comments to %s", len(comments), path)
    return len(comments)
