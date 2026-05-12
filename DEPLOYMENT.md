# Deployment Guide (Step-by-Step)

## 1) Prepare WordPress
1. Enable REST API access (default in modern WordPress).
2. Create a dedicated automation user.
3. Create an **Application Password** for that user.
4. Confirm user permissions for posts, tags/categories, and media uploads.
5. Verify timezone and permalink settings in WordPress admin.

## 2) Configure Repository
1. Add GitHub Secrets:
   - `GEMINI_API_KEY`
   - `PEXELS_API_KEY`
   - `WORDPRESS_URL`
   - `WORDPRESS_USERNAME`
   - `WORDPRESS_APP_PASSWORD`
   - `SLACK_WEBHOOK_URL` (optional)
2. Add GitHub Variables (optional defaults):
   - `WORDPRESS_DEFAULT_CATEGORIES`
   - `WORDPRESS_POST_STATUS`
   - `DRY_RUN`, `BATCH_SIZE`, `MAX_RETRIES`, `REQUEST_TIMEOUT`

## 3) Seed Topics
1. Edit `config/topics.csv`.
2. Set rows you want to process with `status=Generate`.

## 4) Validate Locally
1. `PYTHONPATH=src python -m unittest discover -s tests -v`
2. Dry run:
   - `PYTHONPATH=src python -m wordpress_ai_automation --env dev run`

## 5) Run in GitHub Actions
1. Trigger `Publish WordPress Content` workflow manually.
2. Start with `environment=dev`, `command=run`.
3. Review output and generated state updates.

## 6) Publish to Production
1. Set production settings (`DRY_RUN=false`).
2. Trigger workflow with `environment=prod`.
3. Validate published posts, tags, links, and featured images.
4. Enable/keep daily schedule in `publish.yml` if desired.

## 7) Monitor & Tune
1. Watch logs for errors/rate limits.
2. Tune prompt quality, retries, and batch size.
3. Reprocess failed rows using `docs/RUNBOOK_REPROCESS.md`.
