#!/usr/bin/env python3
"""
Schedule computation for content by niche.
Produces canonical publish times at generation.

Niche schedule:
- DS → Thu 6 PM long-form · Wed 12 PM LinkedIn · Wed 1 PM Twitter · Wed 8 AM IG/FB (week+1) · Wed 8 PM Threads (week+1)
- Life → Tue 2 PM long-form · Mon 12 PM LinkedIn · Mon 1 PM Twitter · Tue 8 AM IG/FB (week+1) · Tue 8 PM Threads (week+1)
- Poetry → Fri 3 PM long-form · Fri 11 AM LinkedIn · Fri 12 PM Twitter · Fri 10 AM IG/FB (week+1) · Fri 12 PM Threads (week+1)
- Shorts: 14 slots Mon–Sun starting next Monday after generation
"""

import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone, date
from pathlib import Path

IST = timezone(timedelta(hours=5, minutes=30))

DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")


def get_iso_week(date_str: str) -> str:
	"""Return 'YYYY-Wnn' from a YYYY-MM-DD string. Uses ISO year, not calendar year."""
	d = date.fromisoformat(date_str)
	iso_year, iso_week, _ = d.isocalendar()
	return f"{iso_year}-W{iso_week:02d}"


# Validate get_iso_week against known mappings
assert get_iso_week("2026-05-12") == "2026-W20", "2026-05-12 should be W20"
assert get_iso_week("2026-05-16") == "2026-W20", "2026-05-16 should be W20"
assert get_iso_week("2026-05-21") == "2026-W21", "2026-05-21 should be W21"
assert get_iso_week("2026-05-25") == "2026-W22", "2026-05-25 should be W22"
assert get_iso_week("2026-06-01") == "2026-W23", "2026-06-01 should be W23"
assert get_iso_week("2026-06-04") == "2026-W23", "2026-06-04 should be W23"
assert get_iso_week("2026-06-08") == "2026-W24", "2026-06-08 should be W24"


def next_weekday(weekday: int, hour: int, minute: int = 0, week_offset: int = 0) -> datetime:
    """
    Return next occurrence of weekday (0=Mon…6=Sun) at given hour:minute IST.
    week_offset=1 shifts result forward by 7 days.
    """
    now = datetime.now(IST)
    days_ahead = weekday - now.weekday()
    if days_ahead < 0:
        days_ahead += 7
    elif days_ahead == 0 and now.hour >= hour:
        days_ahead = 7
    target = now + timedelta(days=days_ahead + week_offset * 7)
    return target.replace(hour=hour, minute=minute, second=0, microsecond=0)


@dataclass
class ShortSlot:
    """Represents a single YouTube short publishing slot."""
    slot: int
    publish_at: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LongFormSchedule:
    """Long-form video schedule."""
    platform: str
    publish_at: str
    channel: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BlogSchedule:
    """Blog/newsletter publish times."""
    substack_publish_at: str
    medium_publish_at: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SocialSchedule:
    """Social media publish times."""
    linkedin_publish_at: str
    twitter_publish_at: str
    ig_fb_publish_at: str
    threads_publish_at: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ContentSchedule:
    """Complete schedule for a piece of content."""
    slug: str
    niche: str
    generated_at: str
    long_form: dict
    blog: dict
    social: dict
    shorts: list[dict]

    def to_dict(self) -> dict:
        return {
            "slug": self.slug,
            "niche": self.niche,
            "generated_at": self.generated_at,
            "long_form": self.long_form,
            "blog": self.blog,
            "social": self.social,
            "shorts": self.shorts,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# Per-niche schedule definitions (weekday 0=Mon, times IST)
NICHE_TIMES = {
    "ds": {
        "long_form": (3, 18, 0),  # Thu 6 PM
        "linkedin": (2, 12, 0),   # Wed 12 PM
        "twitter": (2, 13, 0),    # Wed 1 PM
        "ig_fb": (2, 8, 0),       # Wed 8 AM (week+1)
        "threads": (2, 20, 0),    # Wed 8 PM (week+1)
    },
    "life": {
        "long_form": (1, 14, 0),  # Tue 2 PM
        "linkedin": (0, 12, 0),   # Mon 12 PM
        "twitter": (0, 13, 0),    # Mon 1 PM
        "ig_fb": (1, 8, 0),       # Tue 8 AM (week+1)
        "threads": (1, 20, 0),    # Tue 8 PM (week+1)
    },
    "poetry": {
        "long_form": (4, 15, 0),  # Fri 3 PM
        "linkedin": (4, 11, 0),   # Fri 11 AM
        "twitter": (4, 12, 0),    # Fri 12 PM
        "ig_fb": (4, 10, 0),      # Fri 10 AM (week+1)
        "threads": (4, 12, 0),    # Fri 12 PM (week+1)
    },
}

# YouTube channel mapping
NICHE_CHANNELS = {
    "ds": "Breath of Data Science",
    "life": "Breath of Life",
    "poetry": "Breath of Poetry",
}


def compute(slug: str, niche: str, generation_time: datetime | None = None) -> ContentSchedule:
    """
    Compute complete schedule for a content slug.

    Args:
        slug: content slug (e.g. "2026-05-21_data_science_tech_...")
        niche: "ds", "life", or "poetry"
        generation_time: when content was generated (defaults to now)

    Returns:
        ContentSchedule with all publish times.
    """
    if niche not in NICHE_TIMES:
        raise ValueError(f"Unknown niche: {niche}. Expected: ds, life, poetry")

    if generation_time is None:
        generation_time = datetime.now(IST)

    times = NICHE_TIMES[niche]
    channel = NICHE_CHANNELS[niche]

    # Blog/Substack (week+0) — same day/time as long-form but published this week
    lf_weekday, lf_hour, lf_minute = times["long_form"]
    blog_publish = next_weekday(lf_weekday, lf_hour, lf_minute)  # No week_offset
    blog_social = BlogSchedule(
        substack_publish_at=blog_publish.isoformat(),
        medium_publish_at=(blog_publish + timedelta(minutes=5)).isoformat(),
    )

    # Long-form video (week+1)
    lf_publish = next_weekday(lf_weekday, lf_hour, lf_minute, week_offset=1)

    long_form = LongFormSchedule(
        platform="youtube",
        publish_at=lf_publish.isoformat(),
        channel=channel,
    )

    # Social (all week+1: LinkedIn, Twitter, IG/FB, Threads)
    li_weekday, li_hour, li_minute = times["linkedin"]
    tw_weekday, tw_hour, tw_minute = times["twitter"]
    ig_weekday, ig_hour, ig_minute = times["ig_fb"]
    th_weekday, th_hour, th_minute = times["threads"]

    social = SocialSchedule(
        linkedin_publish_at=next_weekday(li_weekday, li_hour, li_minute, week_offset=1).isoformat(),
        twitter_publish_at=next_weekday(tw_weekday, tw_hour, tw_minute, week_offset=1).isoformat(),
        ig_fb_publish_at=next_weekday(ig_weekday, ig_hour, ig_minute, week_offset=1).isoformat(),
        threads_publish_at=next_weekday(th_weekday, th_hour, th_minute, week_offset=1).isoformat(),
    )

    # Shorts: 14 slots Mon–Sun, starting next Monday of week+1
    shorts: list[dict] = []
    monday_next = next_weekday(0, 10, 0, week_offset=1)  # Monday of next week
    for slot_num in range(14):
        day_offset = slot_num // 2
        is_pm = slot_num % 2 == 1
        slot_hour = 20 if is_pm else 10
        slot_time = monday_next + timedelta(days=day_offset)
        slot_time = slot_time.replace(hour=slot_hour, minute=0, second=0, microsecond=0)
        shorts.append({
            "slot": slot_num,
            "publish_at": slot_time.isoformat(),
        })

    return ContentSchedule(
        slug=slug,
        niche=niche,
        generated_at=generation_time.isoformat(),
        long_form=long_form.to_dict(),
        blog=blog_social.to_dict(),
        social=social.to_dict(),
        shorts=shorts,
    )


def write_schedule_json(slug: str, niche: str, output_dir: Path) -> Path:
    """
    Compute and write schedule.json to output_dir/YYYY-Wnn/{slug}/.

    Args:
        slug: content slug (format: YYYY-MM-DD_niche_...)
        niche: ds/life/poetry
        output_dir: parent dir (typically content/derivatives)

    Returns:
        Path to written schedule.json
    """
    schedule = compute(slug, niche)
    date_str = slug[:10]  # Extract YYYY-MM-DD from slug
    week = get_iso_week(date_str)
    slug_dir = output_dir / week / slug
    slug_dir.mkdir(parents=True, exist_ok=True)
    schedule_path = slug_dir / "schedule.json"
    schedule_path.write_text(schedule.to_json(), encoding="utf-8")
    return schedule_path
