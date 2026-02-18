#!/bin/bash
###############################################################################
# Download TruffleHog binary (Linux x86_64) into bin/.
# The binary is bundled with the DAB since clusters can't reach GitHub.
# Run this before `databricks bundle deploy`.
###############################################################################
set -euo pipefail

BIN_DIR="$(dirname "$0")/bin"
mkdir -p "$BIN_DIR"

VERSION=$(curl -sL https://api.github.com/repos/trufflesecurity/trufflehog/releases/latest \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['tag_name'].lstrip('v'))")

echo "==> Downloading TruffleHog v${VERSION} for Linux x86_64 ..."
curl -sL "https://github.com/trufflesecurity/trufflehog/releases/download/v${VERSION}/trufflehog_${VERSION}_linux_amd64.tar.gz" \
  | tar xz -C "$BIN_DIR" trufflehog

chmod +x "$BIN_DIR/trufflehog"
echo "==> Downloaded: $BIN_DIR/trufflehog ($(du -h "$BIN_DIR/trufflehog" | cut -f1))"
echo ""
echo "==> Now run: databricks bundle deploy --target dev"
