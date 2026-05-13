#!/usr/bin/env python3
"""Build a weekly activity report across the three platform repos.

For each repo, list pull requests merged in the lookback window. Output a
single JSON file consumed by post-weekly-report.py.

Requires the `gh` CLI on PATH and two tokens in the environment:
  - SELF_TOKEN  read access to the self repo (typically the workflow's
                default GITHUB_TOKEN)
  - CROSS_TOKEN read access to the cross-org/cross-repo siblings
                (typically a GitHub App installation token)
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

SELF_REPO = "oslokommune/padda-golden-path"
CROSS_REPOS = [
    "oslokommune/padda-iac",
    "oslokommune/padda-databrikker",
]


def fetch_merged_prs(repo: str, since_date: str, token: str) -> list[dict]:
    """Return merged PRs with mergedAt >= since_date (YYYY-MM-DD, UTC)."""
    env = os.environ.copy()
    env["GH_TOKEN"] = token
    result = subprocess.run(
        [
            "gh", "pr", "list",
            "--repo", repo,
            "--state", "merged",
            "--search", f"merged:>={since_date}",
            "--json", "number,title,url,mergedAt,author",
            "--limit", "200",
        ],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    prs = json.loads(result.stdout)
    prs.sort(key=lambda p: p.get("mergedAt", ""), reverse=True)
    return prs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since-days", type=int, default=7)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    now = datetime.now(UTC)
    since_dt = now - timedelta(days=args.since_days)
    since_date = since_dt.strftime("%Y-%m-%d")

    self_token = os.environ.get("SELF_TOKEN", "")
    cross_token = os.environ.get("CROSS_TOKEN", "")
    if not self_token or not cross_token:
        print("SELF_TOKEN and CROSS_TOKEN must both be set", file=sys.stderr)
        return 1

    report = {
        "generated_at": now.isoformat(),
        "since": since_dt.isoformat(),
        "since_date": since_date,
        "since_days": args.since_days,
        "repos": [],
    }

    targets = [(SELF_REPO, self_token), *((r, cross_token) for r in CROSS_REPOS)]
    for repo, token in targets:
        prs = fetch_merged_prs(repo, since_date, token)
        report["repos"].append({"name": repo, "merged_prs": prs})
        print(f"{repo}: {len(prs)} merged PRs since {since_date}", file=sys.stderr)

    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
