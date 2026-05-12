# Troubleshooting Matrix

## 401 Unauthorized (WordPress)
- Verify `WORDPRESS_USERNAME` and `WORDPRESS_APP_PASSWORD`.
- Confirm user has permission to upload media and publish posts.
- Ensure WordPress site allows application-password auth.

## Media Upload Failure
- Ensure site accepts REST media uploads (`/wp-json/wp/v2/media`).
- Validate remote image URL is accessible.
- Check server upload size and MIME restrictions.

## Taxonomy Mapping Errors
- Confirm categories/tags endpoint permissions.
- Remove unsupported characters from category/tag names.

## Timeout / Rate Limit
- Increase `REQUEST_TIMEOUT` and `MAX_RETRIES`.
- Reduce `BATCH_SIZE`.
- Re-run failed rows after a cool-down period.
