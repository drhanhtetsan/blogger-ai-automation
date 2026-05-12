# Secrets Checklist

Required secrets:
- `GEMINI_API_KEY`
- `PEXELS_API_KEY` (optional but recommended)
- `WORDPRESS_URL`
- `WORDPRESS_USERNAME`
- `WORDPRESS_APP_PASSWORD`

Optional:
- `SLACK_WEBHOOK_URL`

GitHub configuration:
1. Add required values to repository **Secrets and variables > Actions**.
2. Set non-sensitive defaults in repository Variables:
   - `WORDPRESS_DEFAULT_CATEGORIES`
   - `WORDPRESS_POST_STATUS`
   - `DRY_RUN`
   - `BATCH_SIZE`, `MAX_RETRIES`, `REQUEST_TIMEOUT`
