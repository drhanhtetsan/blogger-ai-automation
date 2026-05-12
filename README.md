# WordPress AI Automation

A Python-based automation scaffold to generate SEO blog drafts with AI, enrich posts with stock images + alt text, and publish/schedule to WordPress via REST API.

## What this implementation includes

- AI generation for: title, HTML body, tags, meta description
- Pexels image lookup + AI alt text
- WordPress REST publishing with:
  - application-password authentication
  - media upload
  - categories/tags mapping
  - duplicate slug/title prevention
- CSV state tracking with statuses:
  - `Generate`, `Draft`, `Published`, `Error`
- Retry/backoff for transient API failures
- HTML safety checks before publishing
- Optional comments sync to CSV
- GitHub Actions:
  - CI (`.github/workflows/ci.yml`)
  - Scheduled/manual publish (`.github/workflows/publish.yml`)

## Repository layout

- `src/wordpress_ai_automation/` automation modules
- `config/` state CSV + environment templates
- `workflows/` workflow documentation pointer
- `.github/workflows/` runnable GitHub Actions workflows
- `docs/` setup, ops, troubleshooting, rollback, migration
- `.env.example` local environment template
- `DEPLOYMENT.md` end-to-end deployment steps

## Quick start

1. Copy `.env.example` to `.env` and fill values.
2. Copy an env template:
   - `cp config/environments/dev.env.example config/environments/dev.env`
3. Edit `config/topics.csv` and set `status=Generate`.
4. Run dry-run:
   - `PYTHONPATH=src python -m wordpress_ai_automation --env dev run`
5. Run tests:
   - `PYTHONPATH=src python -m unittest discover -s tests -v`

For full deployment, follow `DEPLOYMENT.md`.
