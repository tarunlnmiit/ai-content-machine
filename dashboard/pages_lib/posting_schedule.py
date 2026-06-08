"""Posting schedule page — weekly publishing times per niche and platform."""
from datetime import date, timedelta
from pathlib import Path

import streamlit as st

# ── Constants ─────────────────────────────────────────────────────────────────

NICHE_EMOJI = {"DS": "🔵", "Life": "🟢", "Poetry": "🟣"}
NICHE_LABEL = {
    "DS": "Data Science",
    "Life": "Life & Self-Dev",
    "Poetry": "Poetry/Quotes",
}

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# day_offset=0 → Monday of current week
# week_offset=0 → current week (long-form), week_offset=1 → following week (social)
LONG_FORM: list[dict] = [
    # ── Week N: Long-form + Blog
    {"day": 1, "time": "14:00", "niche": "Life",   "platforms": ["YouTube", "Substack", "Medium"], "type": "Long-form + Blog", "week": 0},
    {"day": 3, "time": "18:00", "niche": "DS",     "platforms": ["YouTube", "Substack", "Medium"], "type": "Long-form + Blog", "week": 0},
    {"day": 4, "time": "15:00", "niche": "Poetry", "platforms": ["YouTube", "Substack", "Medium"], "type": "Long-form + Blog", "week": 0},
    # ── Week N: LinkedIn (same week — auto via scheduler.py)
    {"day": 1, "time": "08:00", "niche": "Life",   "platforms": ["LinkedIn"],  "type": "LinkedIn post (auto)", "week": 0},
    {"day": 1, "time": "08:00", "niche": "DS",     "platforms": ["LinkedIn"],  "type": "LinkedIn post (auto)", "week": 0},
    {"day": 1, "time": "08:00", "niche": "Poetry", "platforms": ["LinkedIn"],  "type": "LinkedIn post (auto)", "week": 0},
    # ── Week N+1: Twitter (manual — reminders set for Mon 1PM and Fri 12PM)
    {"day": 0, "time": "13:00", "niche": "Life",   "platforms": ["Twitter/X"], "type": "Twitter thread (manual)", "week": 1},
    {"day": 2, "time": "13:00", "niche": "DS",     "platforms": ["Twitter/X"], "type": "Twitter thread (manual)", "week": 1},
    {"day": 4, "time": "12:00", "niche": "Poetry", "platforms": ["Twitter/X"], "type": "Twitter thread (manual)", "week": 1},
    # ── Week N+1: IG + FB (Metricool CSV)
    {"day": 1, "time": "08:00", "niche": "Life",   "platforms": ["Instagram", "Facebook"], "type": "IG carousel (Metricool)", "week": 1},
    {"day": 2, "time": "08:00", "niche": "DS",     "platforms": ["Instagram", "Facebook"], "type": "IG carousel (Metricool)", "week": 1},
    {"day": 4, "time": "10:00", "niche": "Poetry", "platforms": ["Instagram", "Facebook"], "type": "IG carousel (Metricool)", "week": 1},
    # ── Week N+1: Threads (Metricool CSV)
    {"day": 1, "time": "20:00", "niche": "Life",   "platforms": ["Threads"], "type": "Threads post (Metricool)", "week": 1},
    {"day": 2, "time": "20:00", "niche": "DS",     "platforms": ["Threads"], "type": "Threads post (Metricool)", "week": 1},
    {"day": 4, "time": "12:00", "niche": "Poetry", "platforms": ["Threads"], "type": "Threads post (Metricool)", "week": 1},
]

# (day_offset, time_str, label)
SHORTS_SLOTS: list[tuple[int, str, str]] = [
    (0, "10:00", "short_00"), (0, "20:00", "short_01"),
    (1, "10:00", "short_02"), (1, "20:00", "short_03"),
    (2, "10:00", "short_04"), (2, "20:00", "short_05"),
    (3, "10:00", "short_06"), (3, "21:00", "short_07"),  # Thu 9 PM
    (4, "10:00", "short_08"), (4, "20:00", "short_09"),
    (5, "10:00", "short_10"), (5, "20:00", "short_11"),
    (6, "10:00", "short_12"), (6, "20:00", "short_13"),
]

# Long-form publish day per niche (for ★ annotation)
LONG_FORM_DAY = {"Life": 1, "DS": 3, "Poetry": 4}

# ── Helpers ───────────────────────────────────────────────────────────────────

def _week_monday() -> date:
    today = date.today()
    return today - timedelta(days=today.weekday())


def _fmt_time(t: str) -> str:
    h, m = map(int, t.split(":"))
    suffix = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d} {suffix}"


def _build_day_events(niche_filter: set[str]) -> dict[int, list[dict]]:
    """Return day_offset → sorted list of event dicts."""
    events: dict[int, list[dict]] = {d: [] for d in range(7)}

    # Long-form / social events
    seen_shorts_header: dict[int, set[str]] = {d: set() for d in range(7)}
    for e in LONG_FORM:
        if e["niche"] not in niche_filter:
            continue
        if e["type"] == "Shorts tease":
            continue  # handled below
        events[e["day"]].append({
            "time": e["time"],
            "niche": e["niche"],
            "platforms": e["platforms"],
            "type": e["type"],
        })

    # Shorts events — one row per (day, niche) with all slots that day
    shorts_by_day_niche: dict[tuple[int, str], list[tuple[str, str]]] = {}
    for niche in ["DS", "Life", "Poetry"]:
        if niche not in niche_filter:
            continue
        lf_day = LONG_FORM_DAY[niche]
        for slot_i, (day, time, label) in enumerate(SHORTS_SLOTS):
            key = (day, niche)
            shorts_by_day_niche.setdefault(key, [])
            star = " ★" if slot_i * 2 // 2 == lf_day and time == "20:00" else ""  # first post-longform slot
            shorts_by_day_niche[key].append((time, label + star))

    # For each (day, niche) emit two rows (10AM slot and 8/9PM slot)
    for (day, niche), slots in shorts_by_day_niche.items():
        lf_day = LONG_FORM_DAY[niche]
        for time, label in slots:
            star = " ★" if day == lf_day and "★" in label else ""
            phase = "post-long-form" if day > lf_day or (day == lf_day and "★" in label) else "tease"
            events[day].append({
                "time": time,
                "niche": niche,
                "platforms": [f"YouTube Shorts ({label.strip()})"],
                "type": f"Short — {phase}",
            })

    for d in events:
        events[d].sort(key=lambda x: x["time"])

    return events


# ── Render ────────────────────────────────────────────────────────────────────

def render(repo: Path) -> None:
    st.title("📅 Posting Schedule")

    monday = _week_monday()
    week_end = monday + timedelta(days=6)
    next_monday = monday + timedelta(weeks=1)
    next_week_end = next_monday + timedelta(days=6)
    st.caption(
        f"Long-form week: {monday.strftime('%b %d')} – {week_end.strftime('%b %d')} · "
        f"Social week: {next_monday.strftime('%b %d')} – {next_week_end.strftime('%b %d, %Y')} (IST)"
    )
    st.info("**Pivot:** IG · Facebook · Threads · Twitter publish the week AFTER YouTube/Substack/Medium. LinkedIn only is same week (auto).", icon="🔄")

    # ── Filters
    col_a, col_b = st.columns([3, 2])
    with col_a:
        selected_niches = st.multiselect(
            "Niches",
            options=["DS", "Life", "Poetry"],
            default=["DS", "Life", "Poetry"],
            format_func=lambda n: f"{NICHE_EMOJI[n]} {NICHE_LABEL[n]}",
        )
    with col_b:
        compact = st.toggle("Compact view", value=False)

    if not selected_niches:
        st.info("Select at least one niche.")
        return

    niche_set = set(selected_niches)

    # ── Summary table (always shown)
    st.subheader("Long-form & Social — Fixed Times")
    rows = []
    for e in LONG_FORM:
        if e["niche"] not in niche_set:
            continue
        week_offset = e.get("week", 0)
        base = monday + timedelta(weeks=week_offset)
        day_date = base + timedelta(days=e["day"])
        week_tag = "" if week_offset == 0 else " *(+1 wk)*"
        rows.append({
            "Week": "N" if week_offset == 0 else "N+1",
            "Niche": f"{NICHE_EMOJI[e['niche']]} {NICHE_LABEL[e['niche']]}",
            "Day": f"{DAY_NAMES[e['day']]} {day_date.strftime('%b %d')}",
            "Time (IST)": _fmt_time(e["time"]),
            "Platforms": " · ".join(e["platforms"]),
            "Type": e["type"],
        })

    if rows:
        import pandas as pd
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

    # ── Shorts grid
    st.subheader("YouTube Shorts — 2/day × 7 days (all niches)")
    short_rows = []
    lf_days = {"DS": 3, "Life": 1, "Poetry": 4}
    for slot_i, (day, time, label) in enumerate(SHORTS_SLOTS):
        day_date = monday + timedelta(days=day)
        row = {
            "Slot": label,
            "Day": f"{DAY_NAMES[day]} {day_date.strftime('%b %d')}",
            "Time (IST)": _fmt_time(time),
        }
        for niche in ["DS", "Life", "Poetry"]:
            if niche not in niche_set:
                continue
            is_first_post_lf = (day == lf_days[niche] and slot_i % 2 == 1)
            is_post_lf = day > lf_days[niche] or is_first_post_lf
            tag = "★ post-lf" if is_first_post_lf else ("post-lf" if is_post_lf else "tease")
            row[f"{NICHE_EMOJI[niche]} {niche}"] = tag
        short_rows.append(row)

    if short_rows:
        import pandas as pd
        sdf = pd.DataFrame(short_rows)
        st.dataframe(sdf, use_container_width=True, hide_index=True)
        st.caption("★ = first slot after long-form goes live. Add video URL to descriptions retroactively via YouTube Studio.")

    if compact:
        return

    # ── Day-by-day timeline
    st.subheader("Day-by-day Timeline")
    events = _build_day_events(niche_set)

    tabs = st.tabs([f"{DAY_NAMES[d]} {(monday + timedelta(days=d)).strftime('%-d')}" for d in range(7)])

    for d, tab in enumerate(tabs):
        with tab:
            day_events = events[d]
            if not day_events:
                st.caption("Nothing scheduled.")
                continue

            # Group short slots — show as one line per (time, niche) rather than exploded
            seen = set()
            for ev in day_events:
                key = (ev["time"], ev["niche"], ev["type"])
                if key in seen:
                    continue
                seen.add(key)
                emoji = NICHE_EMOJI[ev["niche"]]
                niche_lbl = NICHE_LABEL[ev["niche"]]
                platforms = " · ".join(ev["platforms"])
                is_big = "Long-form" in ev["type"]
                time_str = _fmt_time(ev["time"])
                if is_big:
                    st.markdown(
                        f"**{time_str}** &nbsp; {emoji} **{niche_lbl}** — {ev['type']}  \n"
                        f"&nbsp;&nbsp;&nbsp;&nbsp;`{platforms}`"
                    )
                else:
                    st.markdown(
                        f"{time_str} &nbsp; {emoji} {niche_lbl} — {ev['type']}  \n"
                        f"&nbsp;&nbsp;&nbsp;&nbsp;{platforms}"
                    )
