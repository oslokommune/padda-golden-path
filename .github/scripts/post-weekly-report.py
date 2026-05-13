#!/usr/bin/env python3
"""Format the weekly report as a Slack message and post it.

Input JSON shape (written by build-weekly-report.py):
  {
    "since_date": "YYYY-MM-DD",
    "since_days": 7,
    "repos": [
      {
        "name": "owner/repo",
        "merged_prs": [
          {"number": 42, "title": "...", "url": "...",
           "mergedAt": "...", "author": {"login": "..."}}
        ]
      }
    ]
  }

In --dry-run mode the payload is printed to stdout and nothing is sent.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path


def build_payload(report: dict) -> dict:
    since_days = report.get("since_days", 7)
    since_date = report.get("since_date", "")
    repos = report.get("repos", [])
    total = sum(len(r.get("merged_prs", [])) for r in repos)

    blocks: list[dict] = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Ukentlig plattformrapport — siste {since_days} dager",
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": (
                        f"Sammenslåtte PR-er siden {since_date} "
                        f"· totalt {total} på tvers av repoene"
                    ),
                }
            ],
        },
        {"type": "divider"},
    ]

    for repo_block in repos:
        full_name = repo_block.get("name", "")
        short_name = full_name.split("/")[-1] or full_name
        prs = repo_block.get("merged_prs", [])
        repo_url = f"https://github.com/{full_name}"

        if not prs:
            blocks.append(
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"*<{repo_url}|{short_name}>*\n"
                            "_Ingen sammenslåtte PR-er denne uken._"
                        ),
                    },
                }
            )
            continue

        lines = [f"*<{repo_url}|{short_name}>* — {len(prs)} sammenslåtte PR-er"]
        for pr in prs:
            number = pr.get("number")
            title = pr.get("title", "(uten tittel)")
            url = pr.get("url", "")
            author = (pr.get("author") or {}).get("login") or "ukjent"
            lines.append(f"• <{url}|#{number}> {title} — @{author}")

        blocks.append(
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "\n".join(lines)},
            }
        )

    return {"blocks": blocks}


def post(webhook: str, payload: dict) -> None:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook,
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        if resp.status >= 300 or body.strip() != "ok":
            raise RuntimeError(f"Slack responded {resp.status}: {body}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True, type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    report = json.loads(args.report.read_text())
    payload = build_payload(report)

    repos = report.get("repos", [])
    total = sum(len(r.get("merged_prs", [])) for r in repos)
    print(
        f"Built report for {len(repos)} repos, {total} merged PRs total",
        file=sys.stderr,
    )

    if args.dry_run:
        print("--- dry-run payload ---")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    webhook = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not webhook:
        print("SLACK_WEBHOOK_URL is not set", file=sys.stderr)
        return 1

    post(webhook, payload)
    print("Posted weekly report to Slack", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
