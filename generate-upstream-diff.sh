#!/bin/bash
# generate-upstream-diff.sh
# Clones the upstream Databricks SAT repo and generates a diff report
# against the local bundles/sat-tool/ directory.
#
# Run from the root of the padda-golden-path repo.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
LOCAL_SAT="$REPO_ROOT/bundles/sat-tool"
UPSTREAM_URL="https://github.com/databricks-industry-solutions/security-analysis-tool.git"
TMP_DIR=$(mktemp -d)
UPSTREAM_DIR="$TMP_DIR/security-analysis-tool"
OUTPUT="$LOCAL_SAT/UPSTREAM_DIFF.md"

echo "=== Cloning upstream SAT repo ==="
git clone --depth=1 "$UPSTREAM_URL" "$UPSTREAM_DIR"
UPSTREAM_HASH=$(git -C "$UPSTREAM_DIR" rev-parse --short HEAD)
UPSTREAM_DATE=$(git -C "$UPSTREAM_DIR" log -1 --format='%ci')

echo ""
echo "=== Generating diff report ==="

# Find the upstream src directory (typically src/ or src/dabs/)
UPSTREAM_SRC=""
for candidate in "$UPSTREAM_DIR/src/dabs" "$UPSTREAM_DIR/src" "$UPSTREAM_DIR"; do
    if [ -d "$candidate/notebooks" ] || [ -d "$candidate/Notebooks" ]; then
        UPSTREAM_SRC="$candidate"
        break
    fi
done

if [ -z "$UPSTREAM_SRC" ]; then
    # Try to find notebooks anywhere
    NOTEBOOKS_DIR=$(find "$UPSTREAM_DIR" -type d -iname "notebooks" -maxdepth 3 | head -1)
    if [ -n "$NOTEBOOKS_DIR" ]; then
        UPSTREAM_SRC=$(dirname "$NOTEBOOKS_DIR")
    else
        UPSTREAM_SRC="$UPSTREAM_DIR"
    fi
fi

echo "Upstream source directory: $UPSTREAM_SRC"
echo "Local SAT directory: $LOCAL_SAT"

cat > "$OUTPUT" << EOF
# Upstream Diff: Local SAT Tool vs Databricks SAT

**Generated:** $(date -u '+%Y-%m-%d %H:%M UTC')
**Upstream repo:** $UPSTREAM_URL
**Upstream commit:** $UPSTREAM_HASH ($UPSTREAM_DATE)
**Local SAT SDK version:** 0.1.38

---

## Upstream Directory Structure

\`\`\`
$(cd "$UPSTREAM_DIR" && find . -type f -not -path './.git/*' | sort | head -200)
\`\`\`

## Local Directory Structure

\`\`\`
$(cd "$LOCAL_SAT" && find . -type f -not -path './.git/*' -not -path './wheels/*' -not -path './bin/*' | sort)
\`\`\`

---

## File Comparison

### Files only in local (added/customized)
EOF

# Compare file lists (excluding wheels, bin, .git)
LOCAL_FILES=$(cd "$LOCAL_SAT" && find . -type f -not -path './.git/*' -not -path './wheels/*' -not -path './bin/*' | sort)
UPSTREAM_FILES=$(cd "$UPSTREAM_SRC" && find . -type f -not -path './.git/*' -not -path './wheels/*' -not -path './bin/*' | sort 2>/dev/null || echo "")

echo "" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
comm -23 <(echo "$LOCAL_FILES") <(echo "$UPSTREAM_FILES") >> "$OUTPUT" 2>/dev/null || echo "(comparison not possible - different structures)" >> "$OUTPUT"
echo '```' >> "$OUTPUT"

echo "" >> "$OUTPUT"
echo "### Files only in upstream (not included locally)" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
comm -13 <(echo "$LOCAL_FILES") <(echo "$UPSTREAM_FILES") >> "$OUTPUT" 2>/dev/null || echo "(comparison not possible - different structures)" >> "$OUTPUT"
echo '```' >> "$OUTPUT"

echo "" >> "$OUTPUT"
echo "### Files in both (may have modifications)" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo '```' >> "$OUTPUT"
COMMON=$(comm -12 <(echo "$LOCAL_FILES") <(echo "$UPSTREAM_FILES") 2>/dev/null || echo "")
echo "$COMMON" >> "$OUTPUT"
echo '```' >> "$OUTPUT"

# Generate actual diffs for common files
if [ -n "$COMMON" ]; then
    echo "" >> "$OUTPUT"
    echo "---" >> "$OUTPUT"
    echo "" >> "$OUTPUT"
    echo "## Detailed Diffs for Common Files" >> "$OUTPUT"
    echo "" >> "$OUTPUT"

    while IFS= read -r file; do
        if [ -f "$LOCAL_SAT/$file" ] && [ -f "$UPSTREAM_SRC/$file" ]; then
            DIFF_OUTPUT=$(diff -u "$UPSTREAM_SRC/$file" "$LOCAL_SAT/$file" 2>/dev/null || true)
            if [ -n "$DIFF_OUTPUT" ]; then
                echo "### \`$file\`" >> "$OUTPUT"
                echo "" >> "$OUTPUT"
                echo '```diff' >> "$OUTPUT"
                echo "$DIFF_OUTPUT" | head -100 >> "$OUTPUT"
                DIFF_LINES=$(echo "$DIFF_OUTPUT" | wc -l)
                if [ "$DIFF_LINES" -gt 100 ]; then
                    echo "... ($DIFF_LINES total lines, truncated)" >> "$OUTPUT"
                fi
                echo '```' >> "$OUTPUT"
                echo "" >> "$OUTPUT"
            fi
        fi
    done <<< "$COMMON"
fi

echo "" >> "$OUTPUT"
echo "---" >> "$OUTPUT"
echo "" >> "$OUTPUT"
echo "## How to Update from Upstream" >> "$OUTPUT"
echo "" >> "$OUTPUT"
cat >> "$OUTPUT" << 'INSTRUCTIONS'
To incorporate future upstream changes:

1. Clone the upstream repo:
   ```bash
   git clone https://github.com/databricks-industry-solutions/security-analysis-tool.git /tmp/sat-upstream
   ```

2. Compare with local:
   ```bash
   diff -rq /tmp/sat-upstream/src/dabs/notebooks/ bundles/sat-tool/notebooks/
   ```

3. Review and selectively merge changes:
   ```bash
   # For each changed file, review the diff:
   diff -u /tmp/sat-upstream/src/dabs/notebooks/FILE bundles/sat-tool/notebooks/FILE
   ```

4. Re-run this script to update this diff document.
INSTRUCTIONS

# Cleanup
rm -rf "$TMP_DIR"

echo ""
echo "=== Done ==="
echo "Report saved to: $OUTPUT"
echo "Upstream commit: $UPSTREAM_HASH"
