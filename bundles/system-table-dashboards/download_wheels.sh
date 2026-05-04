#!/bin/bash
###############################################################################
# Download wheels needed by create_system_table_dashboards.py.
#
# Run locally before `databricks bundle deploy`. The workspace does not need
# outbound internet access; the notebook installs databricks-sdk from this
# bundled wheelhouse.
###############################################################################
set -euo pipefail

WHEELS_DIR="$(cd "$(dirname "$0")" && pwd)/wheels"

echo "==> Downloading Databricks SDK wheels into $WHEELS_DIR ..."
mkdir -p "$WHEELS_DIR"

pip download "databricks-sdk==0.38.0" \
  --dest "$WHEELS_DIR" \
  --platform manylinux2014_x86_64 \
  --python-version 311 \
  --only-binary=:all:

# Fetch common native dependencies for the Python versions used by classic and
# serverless Databricks runtimes. Pure-Python wheels are already covered above.
for pyver in 310 311 312 313 314; do
  echo "  Downloading native wheels for cp${pyver}..."
  pip download protobuf charset-normalizer cffi cryptography \
    --dest "$WHEELS_DIR" \
    --platform manylinux2014_x86_64 \
    --python-version "$pyver" \
    --only-binary=:all: \
    --no-deps
done

echo ""
echo "==> Downloaded:"
ls -1 "$WHEELS_DIR"/*.whl
echo ""
echo "==> Now run: databricks bundle deploy --target dev"
