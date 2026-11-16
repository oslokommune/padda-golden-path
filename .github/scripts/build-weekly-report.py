#!/usr/bin/env python3
"""Build a weekly activity report across the platform repos.

The report covers this repo plus every non-archived repo in the organisation
whose name starts with REPO_PREFIX and that the GitHub App behind CROSS_TOKEN
is installed on. For each repo, list pull requests merged in the lookback
window. Output a single JSON file consumed by post-weekly-report.py.

A new repo shows up in the report as soon as the App is installed on it; a
repo the App is not installed on is invisible to this script.

Requires the `gh` CLI on PATH and two tokens in the environment:
  - SELF_TOKEN  read access to the self repo (typically the workflow's
                default GITHUB_TOKEN)
  - CROSS_TOKEN GitHub App installation token with "Pull requests: Read" on
                the sibling repos
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

OWNER = "oslokommune"
REPO_PREFIX = "padda-"
SELF_REPO = f"{OWNER}/padda-golden-path"


def run_gh(args: list[str], token: str) -> str:
    """Run a gh command with the given token and return its stdout."""
    env = os.environ.copy()
    env["GH_TOKEN"] = token
    result = subprocess.run(
        ["gh", *args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    if result.returncode != 0:
        msg = f"gh {' '.join(args)} failed: {result.stderr.strip()}"
        raise RuntimeError(msg)
    return result.stdout


def discover_cross_repos(token: str) -> list[str]:
    """Return sibling repos the App installation can access, sorted by name."""
    out = run_gh(
        [
            "api",
            "installation/repositories",
            "--paginate",
            "--jq",
            ".repositories[] | select(.archived | not) | .full_name",
        ],
        token,
    )
    prefix = f"{OWNER}/{REPO_PREFIX}"
    return sorted(
        name for name in out.split() if name.startswith(prefix) and name != SELF_REPO
    )


def assert_can_read_prs(repo: str, token: str) -> None:
    """Fail loudly if the token cannot read pull requests in the repo.

    The search used by fetch_merged_prs silently returns an empty list for
    repos the token cannot read, which would otherwise be reported as
    "no merged PRs".
    """
    run_gh(["api", f"repos/{repo}/pulls?state=closed&per_page=1", "--silent"], token)


def fetch_merged_prs(repo: str, since_date: str, token: str) -> list[dict]:
    """Return merged PRs with mergedAt >= since_date (YYYY-MM-DD, UTC)."""
    env = os.environ.copy()
    env["GH_TOKEN"] = token
    result = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            repo,
            "--state",
            "merged",
            "--search",
            f"merged:>={since_date}",
            "--json",
            "number,title,url,mergedAt,author",
            "--limit",
            "200",
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

    cross_repos = discover_cross_repos(cross_token)
    if not cross_repos:
        print(
            f"No {OWNER}/{REPO_PREFIX}* repos visible to CROSS_TOKEN; "
            "is the GitHub App installed on them?",
            file=sys.stderr,
        )
        return 1

    targets = [(SELF_REPO, self_token), *((r, cross_token) for r in cross_repos)]
    for repo, token in targets:
        assert_can_read_prs(repo, token)
        prs = fetch_merged_prs(repo, since_date, token)
        report["repos"].append({"name": repo, "merged_prs": prs})
        print(f"{repo}: {len(prs)} merged PRs since {since_date}", file=sys.stderr)

    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
