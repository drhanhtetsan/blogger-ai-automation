# Runbook: Reprocess Failed Rows

1. Open `config/topics.csv`.
2. Filter rows where `status=Error`.
3. Fix root cause based on `last_error`.
4. Set `status=Generate` for rows to retry.
5. Re-run:
   - `PYTHONPATH=src python -m wordpress_ai_automation --env prod run`
6. Confirm `status=Published` and `post_url` populated.
