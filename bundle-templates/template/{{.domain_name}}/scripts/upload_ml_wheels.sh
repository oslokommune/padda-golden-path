#!/usr/bin/env bash
# Download the third-party wheels the job needs and upload them to the
# bundle's wheels volume.
#
# Serverless compute on this platform has no internet access, so the job
# installs with `--no-index --find-links /Volumes/.../wheels`. torch is not in
# the serverless base environment; sympy, networkx and mpmath (torch
# dependencies) are not either. Wheels are downloaded for Linux x86_64 and the
# Python version of serverless environment version 6.
#
# Usage: scripts/upload_ml_wheels.sh [target] [profile]
# Run after `databricks bundle deploy` (the volume must exist) and before
# `databricks bundle run`.
set -euo pipefail

TARGET="${1:-dev}"
PROFILE="${2:-${DATABRICKS_CONFIG_PROFILE:-DEFAULT}}"
TORCH_VERSION="2.12.0"   # matches the databricks_ml_v6 base environment
PYTHON_VERSION="3.12"     # serverless environment version 6
PLATFORM="manylinux_2_28_x86_64"

cd "$(dirname "$0")/.."
mkdir -p wheels

if ! ls wheels/torch-*.whl >/dev/null 2>&1; then
  echo "Downloading torch ${TORCH_VERSION}+cpu and dependencies for ${PLATFORM} / cp${PYTHON_VERSION/./}..."
  uv run --with pip python -m pip download \
    --only-binary=:all: \
    --platform "$PLATFORM" \
    --implementation cp \
    --python-version "$PYTHON_VERSION" \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    "torch==${TORCH_VERSION}+cpu" \
    -d wheels/
fi

# The schema name comes from the schema resource: in development mode it is
# prefixed (dev_<user>_...), and the volume's schema_name reference is not
# resolved in the summary output.
VOLUME_PATH=$(databricks bundle summary -t "$TARGET" --profile "$PROFILE" -o json \
  | jq -r '"/Volumes/\(.resources.volumes.example_ml_wheels.catalog_name)/\(.resources.schemas.example_ml_schema.name)/\(.resources.volumes.example_ml_wheels.name)"')
echo "Uploading $(ls wheels | wc -l | tr -d ' ') wheels to ${VOLUME_PATH}/ ..."
databricks fs cp -r --overwrite --profile "$PROFILE" wheels/ "dbfs:${VOLUME_PATH}/"
databricks fs ls --profile "$PROFILE" "dbfs:${VOLUME_PATH}/"
