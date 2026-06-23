"""Publishing checklist page — parses docs/week-N-publishing-checklist.md at render time."""
import json
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

import streamlit as st

from pages_lib._common import copy_button

_MONTHS = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}


@dataclass
class Item:
    label: str
    cmds: list[str] = field(default_factory=list)
    doc_checked: bool = False   # True when doc has [x] — used as fallback default


@dataclass
class Section:
    step_id: str
    title: str
    schedule: Optional[str]
    body: str = ""          # prose/tables/instructions between header and checkboxes
    items: list[Item] = field(default_factory=list)


# ── Parsing ──────────────────────────────────────────────────────────────────

def _normalize_step_id(header_text: str) -> str:
    m = re.search(r"\bSTEP\s+(\w+)", header_text, re.IGNORECASE)
    if m:
        return f"step_{m.group(1).lower()}"
    words = re.sub(r"[^\w\s]", "", header_text).split()[:3]
    return "_".join(w.lower() for w in words) or "section"


def _extract_schedule(header_text: str) -> Optional[str]:
    m = re.search(r"\(([^)]+)\)", header_text)
    return m.group(1) if m else None


def parse_checklist(doc_path: Path) -> list[Section]:
    text = doc_path.read_text(encoding="utf-8")
    sections: list[Section] = []
    current: Optional[Section] = None
    body_lines: list[str] = []
    cmd_buffer: list[str] = []
    in_code = False
    code_lines: list[str] = []

    def _flush_body() -> None:
        if current is not None:
            current.body = "\n".join(body_lines).strip()

    for line in text.splitlines():
        # Code fence handling
        if re.match(r"^```", line):
            if in_code:
                in_code = False
                cmd_buffer.append("\n".join(code_lines))
                code_lines = []
            else:
                in_code = True
                code_lines = []
            continue

        if in_code:
            code_lines.append(line)
            continue

        # Header (## / ### / ####)
        hm = re.match(r"^(#{2,4})\s+(.+)", line)
        if hm:
            _flush_body()
            body_lines = []
            raw_title = hm.group(2)
            clean_title = re.sub(r"\s*\([^)]+\)\s*$", "", raw_title).strip()
            section = Section(
                step_id=_normalize_step_id(raw_title),
                title=clean_title,
                schedule=_extract_schedule(raw_title),
            )
            sections.append(section)
            current = section
            continue

        # Checkbox line — match both unchecked [ ] and checked [x]
        cm = re.match(r"^- \[([x ])\]\s+(.+)", line)
        if cm and current is not None:
            current.items.append(Item(
                label=cm.group(2),
                cmds=list(cmd_buffer),
                doc_checked=cm.group(1) == "x",
            ))
            cmd_buffer.clear()
            continue

        # Everything else: body text (prose, tables, bullets, numbered steps, ---)
        if current is not None:
            body_lines.append(line)

    _flush_body()

    result = [s for s in sections if s.items]
    _redistribute_cmds(result)
    return result


def _redistribute_cmds(sections: list[Section]) -> None:
    """When a section has N items and all N cmds land on item[0], spread them 1:1."""
    for s in sections:
        if len(s.items) < 2:
            continue
        all_cmds = [c for item in s.items for c in item.cmds]
        if len(all_cmds) != len(s.items):
            continue
        if s.items[0].cmds != all_cmds:
            continue
        for i, item in enumerate(s.items):
            item.cmds = [all_cmds[i]]


# ── Week discovery ────────────────────────────────────────────────────────────

def _find_weeks(repo: Path) -> list[str]:
    docs = repo / "docs"
    if not docs.is_dir():
        return []
    pattern = re.compile(r"^week-(\d+)-publishing-checklist\.md$")
    hits = []
    for p in docs.iterdir():
        m = pattern.match(p.name)
        if m:
            hits.append((int(m.group(1)), p.stem.replace("-publishing-checklist", "")))
    hits.sort()
    return [name for _, name in hits]


# ── State persistence ─────────────────────────────────────────────────────────

def _states_path(repo: Path) -> Path:
    return repo / "data" / "checklist_states.json"


def _load_states(repo: Path) -> dict:
    p = _states_path(repo)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _write_states(repo: Path, states: dict) -> None:
    p = _states_path(repo)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(states, indent=2), encoding="utf-8")


def _make_on_change(repo: Path):
    def _cb(key: str) -> None:
        s = _load_states(repo)
        s[key] = st.session_state[key]
        _write_states(repo, s)
    return _cb


# ── Schedule badge ────────────────────────────────────────────────────────────

def _schedule_badge(schedule: Optional[str]) -> str:
    if not schedule:
        return ""
    m = re.search(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2})\b", schedule)
    if not m:
        return ""
    month = _MONTHS[m.group(1)]
    day = int(m.group(2))
    today = date.today()
    year = today.year if month >= today.month else today.year + 1
    try:
        sched = date(year, month, day)
    except ValueError:
        return f"⚪ {schedule}"
    if sched < today:
        return f"🔴 {schedule}"
    if sched == today:
        return f"🟡 {schedule}"
    return f"⚪ {schedule}"


# ── Main render ───────────────────────────────────────────────────────────────

def render(repo: Path) -> None:
    st.title("📋 Publishing Checklist")

    weeks = _find_weeks(repo)
    if not weeks:
        st.info(
            "No checklist docs found. "
            "Generate `docs/week-N-publishing-checklist.md` to get started."
        )
        return

    # ── Top controls row
    ctrl_l, ctrl_m, ctrl_r = st.columns([2, 3, 2])

    with ctrl_l:
        week = st.selectbox("Week", weeks, index=len(weeks) - 1, label_visibility="collapsed",
                            format_func=lambda w: f"Week: {w}")

    doc_path = repo / "docs" / f"{week}-publishing-checklist.md"
    if not doc_path.exists():
        st.error(f"Doc not found: {doc_path}")
        return

    sections = parse_checklist(doc_path)
    states = _load_states(repo)

    total = sum(len(s.items) for s in sections)
    done = sum(
        1 for s in sections for i, item in enumerate(s.items)
        if states.get(f"{week}|{s.step_id}|{i}", item.doc_checked)
    )

    with ctrl_m:
        pct = done / total if total > 0 else 0
        st.progress(pct, text=f"{done} / {total} done")

    with ctrl_r:
        if st.button("↺ Reset week", key="reset_btn"):
            st.session_state["_reset_confirm"] = True

    # ── Reset confirmation
    if st.session_state.get("_reset_confirm"):
        st.warning(f"Clear all checked state for **{week}**? This cannot be undone.")
        yes_col, no_col, _ = st.columns([1, 1, 5])
        with yes_col:
            if st.button("Yes, reset", key="reset_yes", type="primary"):
                prefix = f"{week}|"
                new_states = {k: v for k, v in states.items() if not k.startswith(prefix)}
                _write_states(repo, new_states)
                for k in [k for k in st.session_state if k.startswith(prefix)]:
                    del st.session_state[k]
                st.session_state["_reset_confirm"] = False
                st.rerun()
        with no_col:
            if st.button("Cancel", key="reset_no"):
                st.session_state["_reset_confirm"] = False
                st.rerun()

    # ── Filter toggle
    show_remaining = st.toggle("Show remaining only", value=False, key="show_remaining")

    st.divider()

    on_change = _make_on_change(repo)

    for section in sections:
        badge = _schedule_badge(section.schedule)
        header_md = f"#### {section.title}"
        if badge:
            header_md += f"&nbsp;&nbsp;&nbsp;{badge}"
        st.markdown(header_md)

        # Section body: prose, tables, numbered instructions — collapsed by default
        if section.body:
            with st.expander("ℹ️ Details", expanded=False):
                st.markdown(section.body)

        any_visible = False
        for i, item in enumerate(section.items):
            ck = f"{week}|{section.step_id}|{i}"
            checked = states.get(ck, item.doc_checked)

            if show_remaining and checked:
                continue

            any_visible = True
            st.checkbox(
                item.label,
                value=checked,
                key=ck,
                on_change=on_change,
                args=(ck,),
            )

            if item.cmds:
                with st.expander("▶ Commands"):
                    for j, cmd in enumerate(item.cmds):
                        copy_button(cmd, key=f"copy_{ck}_{j}")

        if show_remaining and not any_visible:
            st.caption("✅ All done in this step")

        st.markdown("")  # spacing between sections
