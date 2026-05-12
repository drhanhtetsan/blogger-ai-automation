# Local Setup Guide

1. Ensure Python 3.11+ is installed.
2. Copy `.env.example` to `.env` and fill in your API credentials.
3. Copy one environment template:
   - `cp config/environments/dev.env.example config/environments/dev.env`
   - `cp config/environments/prod.env.example config/environments/prod.env`
4. Update `config/topics.csv` with topics and status `Generate`.
5. Run dry-run generation:
   - `PYTHONPATH=src python -m wordpress_ai_automation --env dev run`
6. Run publish mode:
   - Set `DRY_RUN=false`
   - `PYTHONPATH=src python -m wordpress_ai_automation --env prod run`
7. Sync comments (optional):
   - `PYTHONPATH=src python -m wordpress_ai_automation --env prod sync-comments`
