#!/bin/bash
###############################################################################
# Download SAT wheels (Linux x86_64) into the wheels/ directory.
# Run this before `databricks bundle deploy`.
###############################################################################
set -euo pipefail

WHEELS_DIR="$(dirname "$0")/wheels"

echo "==> Downloading wheels for Linux x86_64 into $WHEELS_DIR ..."
mkdir -p "$WHEELS_DIR"

# Pure-Python wheels (work on any Python version)
pip download dbl-sat-sdk \
  --dest "$WHEELS_DIR" \
  --platform manylinux2014_x86_64 \
  --python-version 311 \
  --only-binary=:all:

# Platform-specific wheels — download for Python 3.10–3.14
# to cover classic (DBR 13.x = 3.10, DBR 14.x = 3.11) and serverless runtimes.
for pyver in 310 311 312 313 314; do
  echo "  Downloading native wheels for cp${pyver}..."
  pip download PyYAML cffi charset-normalizer \
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
