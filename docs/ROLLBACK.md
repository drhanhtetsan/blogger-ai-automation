# Rollback Procedure

If a bad publish occurs:

1. Disable automation schedule in `.github/workflows/publish.yml`.
2. Set `DRY_RUN=true` in environment variables.
3. In WordPress admin, change affected posts from `publish` to `draft`.
4. In `config/topics.csv`, set impacted rows to `Error` and write reason in `last_error`.
5. Fix prompts/configuration.
6. Re-run in staging first (`--env dev`).
