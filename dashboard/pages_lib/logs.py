"""Logs — tail recent logs."""

from pathlib import Path

import streamlit as st


def render(REPO: Path):
    st.title("📊 Logs")

    LOGS = {
        "scheduler.log": REPO / "data" / "analytics" / "scheduler.log",
        "scheduler.error.log": REPO / "data" / "analytics" / "scheduler.error.log",
        "daily_ideas.log": Path("/tmp/daily_ideas.log"),
        "daily_ideas.error.log": Path("/tmp/daily_ideas.error.log"),
        "build_kb.log": Path("/tmp/build_kb.log"),
        "build_kb.error.log": Path("/tmp/build_kb.error.log"),
        "research_log.txt": REPO / "data" / "analytics" / "research_log.txt",
    }

    cols = st.columns(2)
    n = st.slider("Tail lines", 20, 500, 80)

    for i, (name, path) in enumerate(LOGS.items()):
        with cols[i % 2]:
            with st.expander(f"{name}  ({'exists' if path.exists() else 'missing'})", expanded=False):
                if path.exists():
                    lines = path.read_text().splitlines()
                    st.code("\n".join(lines[-n:]) or "(empty)", language="text")
                else:
                    st.caption(f"`{path}` not found")
