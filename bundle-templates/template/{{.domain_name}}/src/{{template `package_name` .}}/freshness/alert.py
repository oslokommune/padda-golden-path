"""Argument parsing and reporting for the freshness alert (pure Python, no Spark)."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

_THRESHOLD_UNITS = {"m": "minutes", "h": "hours", "d": "days"}
_UNCHECKED_HEADING = (
    "Could not check (wrong table or column name, column not TIMESTAMP,"
    " or missing SELECT permission):"
)


@dataclass(frozen=True)
class WatchedTable:
    """Full table name, load timestamp column and freshness threshold."""

    name: str
    column: str
    threshold: timedelta


@dataclass(frozen=True)
class Observation:
    """Newest load timestamp in UTC (None if no rows), or why it could not be checked."""

    table: WatchedTable
    latest: datetime | None
    error: str | None = None


def parse_threshold(text: str) -> timedelta:
    """Parse a freshness threshold such as ``30m``, ``26h`` or ``8d``."""
    match = re.fullmatch(r"([0-9]+)([mhd])", text)
    if match is None or int(match[1]) == 0:
        msg = (
            f"invalid freshness threshold {text!r}: expected a positive whole number "
            "followed by m, h or d, e.g. 30m, 26h or 8d"
        )
        raise ValueError(msg)
    return timedelta(**{_THRESHOLD_UNITS[match[2]]: int(match[1])})


def parse_args(argv: Sequence[str] | None = None) -> list[WatchedTable]:
    """Return one watched table per ``<table> <column> <threshold>`` entry."""
    parser = argparse.ArgumentParser(description="Fail when watched tables are stale.")
    parser.add_argument(
        "entries",
        nargs="+",
        metavar="ENTRY",
        help=(
            "full table name, load timestamp column and freshness threshold (e.g. 26h),"
            " separated by whitespace"
        ),
    )
    args = parser.parse_args(argv)
    tables = []
    for entry in args.entries:
        values = entry.split()
        if len(values) != 3:
            parser.error(
                f"{entry!r}: expected <table> <load timestamp column> <freshness threshold>"
            )
        name, column, threshold = values
        try:
            tables.append(WatchedTable(name, column, parse_threshold(threshold)))
        except ValueError as exc:
            parser.error(f"{entry!r}: {exc}")
    return tables


def _format_duration(duration: timedelta) -> str:
    minutes = max(int(duration.total_seconds()) // 60, 0)
    days, minutes = divmod(minutes, 24 * 60)
    hours, minutes = divmod(minutes, 60)
    parts = [
        f"{value}{unit}" for value, unit in ((days, "d"), (hours, "h"), (minutes, "m")) if value
    ]
    return " ".join(parts) or "0m"


def _format_threshold(threshold: timedelta) -> str:
    minutes = int(threshold.total_seconds()) // 60
    for unit, size in (("d", 24 * 60), ("h", 60)):
        if minutes % size == 0:
            return f"{minutes // size}{unit}"
    return f"{minutes}m"


def is_stale(observation: Observation, now: datetime) -> bool:
    """Return True if a checked table has no rows or is older than its threshold."""
    latest = observation.latest
    return latest is None or now - latest > observation.table.threshold


def describe(observation: Observation, now: datetime) -> str:
    """Return one line with name, latest load timestamp, age and threshold."""
    table = observation.table
    if observation.error is not None:
        return f"{table.name}: could not check: {observation.error}"
    threshold = _format_threshold(table.threshold)
    if observation.latest is None:
        return f"{table.name}: no rows, threshold {threshold}"
    return (
        f"{table.name}: latest load timestamp {observation.latest:%Y-%m-%d %H:%M} UTC, "
        f"age {_format_duration(now - observation.latest)}, threshold {threshold}"
    )


def build_report(observations: Sequence[Observation], now: datetime) -> str | None:
    """Return every problem in one report, or None if all tables are fresh."""
    checked = [o for o in observations if o.error is None]
    stale = [f"- {describe(o, now)}" for o in checked if is_stale(o, now)]
    unchecked = [f"- {o.table.name}: {o.error}" for o in observations if o.error is not None]
    if not stale and not unchecked:
        return None
    problems = len(stale) + len(unchecked)
    header = (
        f"Freshness alert: {problems} of {len(observations)} watched tables are stale"
        " or could not be checked."
    )
    lines = [header]
    if stale:
        lines += ["", "Stale (no new data within the freshness threshold):", *stale]
    if unchecked:
        lines += ["", _UNCHECKED_HEADING, *unchecked]
    return "\n".join(lines)
