#!/usr/bin/env bash
set -euo pipefail

BUCKET="s3://padda-dev-docs"
DISTRIBUTION_ID="E2YXU00C851J9P"
SOURCE_DIR="site-v2/"

echo "Building docs..."
uv run --extra docs zensical build -f zensical-v2.toml

echo "Syncing ${SOURCE_DIR} to ${BUCKET}..."
aws s3 sync "${SOURCE_DIR}" "${BUCKET}" --delete

echo "Invalidating CloudFront cache..."
INVALIDATION_ID=$(aws cloudfront create-invalidation \
  --distribution-id "${DISTRIBUTION_ID}" \
  --paths "/*" \
  --query "Invalidation.Id" \
  --output text)

echo "Waiting for invalidation ${INVALIDATION_ID}..."
aws cloudfront wait invalidation-completed \
  --distribution-id "${DISTRIBUTION_ID}" \
  --id "${INVALIDATION_ID}"

echo "Done! Site is live."
