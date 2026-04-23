#!/usr/bin/env python3
"""Read Claude's relevance report and post relevant entries to a Slack webhook.

Report format (written by Claude):
  {
    "assessments": [
      {"id": "...", "title": "...", "link": "...",
       "relevant": true|false, "reason": "..."}
    ]
  }

In --dry-run mode the payloads are logged to stdout and nothing is sent.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path


def build_payload(entry: dict) -> dict:
    title = entry.get("title", "(uten tittel)")
    link = entry.get("link", "")
    reason = entry.get("reason", "").strip() or "(ingen begrunnelse)"

    return {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*<{link}|{title}>*",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": reason},
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "Databricks release feed · relevansvurdering av Claude",
                    }
                ],
            },
        ]
    }


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
    assessments = report.get("assessments", [])
    relevant = [a for a in assessments if a.get("relevant")]

    print(
        f"Assessed {len(assessments)} entries, {len(relevant)} flagged relevant",
        file=sys.stderr,
    )

    if not relevant:
        return 0

    webhook = os.environ.get("SLACK_WEBHOOK_URL", "")
    if not args.dry_run and not webhook:
        print("SLACK_WEBHOOK_URL is not set", file=sys.stderr)
        return 1

    for entry in relevant:
        payload = build_payload(entry)
        if args.dry_run:
            print("--- dry-run payload ---")
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            post(webhook, payload)
            print(f"Posted: {entry.get('title', '')[:80]}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
