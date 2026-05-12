# Migration from Blogger Workflow

This project preserves your Blogger pipeline concepts:

- **Topic Queue**: same sheet/CSV-driven queue with `Generate` trigger.
- **Statuses**: `Generate`, `Draft`, `Published`, `Error`.
- **Batching**: controlled by `BATCH_SIZE`.
- **Sync Back**: published URL and error details are written back to state storage.

Migration steps:
1. Export your Blogger topics into `config/topics.csv`.
2. Keep status values as-is.
3. Configure WordPress credentials and categories.
4. Run dry run first (`DRY_RUN=true`).
5. Switch to publish mode when output quality is acceptable.
