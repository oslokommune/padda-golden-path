#!/usr/bin/env python3
"""Fetch the Databricks release-notes feed, filter to entries newer than the
last-seen timestamp, cap the result, and emit two files:

  - new-entries.json   (the payload Claude will assess)
  - new-last-seen.txt  (the timestamp to commit if the run succeeds)

Stdlib only. RSS 2.0 feed with pubDate in RFC 822 format.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree as ET


FEED_URL = "https://docs.databricks.com/aws/en/feed.xml"


def parse_since(value: str) -> datetime | None:
    """Accept ISO 8601 ('2026-04-20T00:00:00Z') or relative ('7 days ago')."""
    value = value.strip()
    if not value:
        return None

    m = re.fullmatch(r"(\d+)\s+days?\s+ago", value, flags=re.IGNORECASE)
    if m:
        return datetime.now(timezone.utc) - timedelta(days=int(m.group(1)))

    # ISO 8601 — tolerate 'Z' suffix
    iso = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def load_state(path: Path) -> datetime | None:
    if not path.exists():
        return None
    text = path.read_text().strip()
    if not text:
        return None
    return parse_since(text)


def strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def fetch_feed(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "databricks-feed-watcher"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8")


def parse_entries(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    channel = root.find("channel")
    if channel is None:
        raise SystemExit("Feed is missing <channel> — unexpected format.")

    entries = []
    for item in channel.findall("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        guid = (item.findtext("guid") or link).strip()
        pub_date_raw = (item.findtext("pubDate") or "").strip()
        description_raw = (item.findtext("description") or "").strip()
        categories = [c.text.strip() for c in item.findall("category") if c.text]

        try:
            pub_date = parsedate_to_datetime(pub_date_raw)
        except (TypeError, ValueError):
            continue
        if pub_date.tzinfo is None:
            pub_date = pub_date.replace(tzinfo=timezone.utc)

        entries.append({
            "id": guid,
            "title": title,
            "link": link,
            "pub_date": pub_date.isoformat(),
            "categories": categories,
            "summary": strip_html(description_raw)[:1200],
        })
    return entries


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--state-file", required=True, type=Path)
    ap.add_argument("--override-since", default="", help="ISO or 'N days ago'")
    ap.add_argument("--max-entries", type=int, default=50)
    ap.add_argument("--output-entries", required=True, type=Path)
    ap.add_argument("--output-new-state", required=True, type=Path)
    args = ap.parse_args()

    if args.override_since.strip():
        since = parse_since(args.override_since)
        source = f"override ({args.override_since!r})"
    else:
        since = load_state(args.state_file)
        source = f"state file ({args.state_file})"

    if since is None:
        # First run or empty state and no override — default to last 3 days.
        since = datetime.now(timezone.utc) - timedelta(days=3)
        source += " → defaulting to last 3 days"

    print(
        f"Filtering entries newer than {since.isoformat()} (from {source})",
        file=sys.stderr,
    )

    xml_text = fetch_feed(FEED_URL)
    all_entries = parse_entries(xml_text)
    print(f"Feed has {len(all_entries)} total entries", file=sys.stderr)

    new_entries = [
        e for e in all_entries if datetime.fromisoformat(e["pub_date"]) > since
    ]
    new_entries.sort(key=lambda e: e["pub_date"], reverse=True)

    if args.max_entries > 0 and len(new_entries) > args.max_entries:
        print(
            f"Capping {len(new_entries)} → {args.max_entries} entries",
            file=sys.stderr,
        )
        new_entries = new_entries[: args.max_entries]

    print(f"Emitting {len(new_entries)} new entries", file=sys.stderr)

    args.output_entries.write_text(
        json.dumps({"entries": new_entries}, ensure_ascii=False, indent=2)
    )

    if new_entries:
        latest = max(e["pub_date"] for e in new_entries)
    else:
        latest = since.isoformat()
    args.output_new_state.write_text(latest + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
