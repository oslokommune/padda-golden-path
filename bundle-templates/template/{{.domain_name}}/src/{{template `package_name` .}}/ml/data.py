"""Synthetic meeting-room bookings.

Everything here is pure pandas/numpy so it can be unit-tested without Spark.
Output is deterministic for a given ``GeneratorConfig.seed``. The booking
probability encodes the signal the model is expected to learn: weekdays and
core hours are busy, small rooms with video are popular, evenings and weekends
are quiet.

Timestamps are naive local time (``Europe/Oslo`` wall-clock), following team
booking's ADR on user-facing times: a 14:00 booking stays 14:00 across DST.
"""

from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

import numpy as np
import pandas as pd

BUILDINGS: list[str] = ["Rådhuset", "Grensen", "Storgata"]
UNITS: list[str] = ["Byrådsavdelingen", "Plan og bygning", "Utdanning", "Helse", "Kultur"]
WORK_HOURS: range = range(7, 18)  # booking start hours 07:00 .. 17:00
DURATIONS_HOURS: list[int] = [1, 1, 1, 2, 2, 3]
DEFAULT_START_DATE = date(2026, 6, 1)  # a Monday

_NORWEGIAN = str.maketrans({"æ": "ae", "ø": "o", "å": "a"})


def slug(text: str) -> str:
    """Return an ASCII snake_case identifier for use in column names."""
    lowered = text.lower().translate(_NORWEGIAN)
    ascii_only = unicodedata.normalize("NFKD", lowered).encode("ascii", "ignore").decode()
    return "_".join(part for part in ascii_only.replace("-", " ").split() if part)


@dataclass(frozen=True)
class GeneratorConfig:
    """Size, period and seed of the synthetic data set."""

    n_rooms: int = 20
    weeks: int = 12
    start_date: date = DEFAULT_START_DATE
    seed: int = 42

    @property
    def end_date_exclusive(self) -> date:
        """First date after the generated period."""
        return self.start_date + timedelta(weeks=self.weeks)


def generate_rooms(cfg: GeneratorConfig) -> pd.DataFrame:
    """Return the ``rom`` table: one row per room with building, floor, capacity, video."""
    rng = np.random.default_rng(cfg.seed)
    return pd.DataFrame(
        {
            "rom_id": [f"rom-{i:03d}" for i in range(1, cfg.n_rooms + 1)],
            "bygg": rng.choice(BUILDINGS, cfg.n_rooms),
            "etasje": rng.integers(1, 7, cfg.n_rooms).astype("int64"),
            "kapasitet": rng.choice([4, 6, 8, 10, 12, 20], cfg.n_rooms).astype("int64"),
            "har_video": rng.random(cfg.n_rooms) < 0.6,
        }
    )


def booking_probability(
    weekday: int, hour: int, kapasitet: int, har_video: bool, bygg: str
) -> float:
    """Return the probability that a booking starts in this room at this hour.

    ``weekday`` is 0=Monday .. 6=Sunday (``date.weekday()``).
    """
    p = 0.12
    if weekday < 5:
        p += 0.22
    if weekday in (1, 2, 3):
        p += 0.08
    if 9 <= hour <= 11 or 13 <= hour <= 14:
        p += 0.22
    if hour < 8 or hour >= 16:
        p -= 0.12
    if kapasitet <= 6:
        p += 0.08
    if kapasitet >= 20:
        p -= 0.08
    if har_video:
        p += 0.06
    if bygg == BUILDINGS[0]:
        p += 0.04
    return float(min(max(p, 0.02), 0.95))


def generate_bookings(rooms: pd.DataFrame, cfg: GeneratorConfig) -> pd.DataFrame:
    """Return the ``bookinger`` table: hourly bookings for every room over the period.

    A room can hold at most one booking at a time: while a booking is running
    no new one is drawn for that room.
    """
    rng = np.random.default_rng(cfg.seed + 1)
    rows: list[dict[str, object]] = []
    for day_offset in range(cfg.weeks * 7):
        day = cfg.start_date + timedelta(days=day_offset)
        for room in rooms.to_dict("records"):
            busy_until = min(WORK_HOURS)
            for hour in WORK_HOURS:
                if hour < busy_until:
                    continue
                p = booking_probability(
                    day.weekday(),
                    hour,
                    int(room["kapasitet"]),
                    bool(room["har_video"]),
                    str(room["bygg"]),
                )
                if rng.random() >= p:
                    continue
                duration = int(rng.choice(DURATIONS_HOURS))
                duration = min(duration, max(WORK_HOURS) + 1 - hour)
                start = datetime.combine(day, time(hour))
                lead = timedelta(days=int(rng.integers(0, 14)), hours=int(rng.integers(1, 9)))
                rows.append(
                    {
                        "rom_id": room["rom_id"],
                        "start": start,
                        "slutt": start + timedelta(hours=duration),
                        "enhet": str(rng.choice(UNITS)),
                        "opprettet": start - lead,
                    }
                )
                busy_until = hour + duration
    bookings = pd.DataFrame(rows, columns=["rom_id", "start", "slutt", "enhet", "opprettet"])
    bookings.insert(0, "booking_id", np.arange(1, len(bookings) + 1, dtype="int64"))
    return bookings
