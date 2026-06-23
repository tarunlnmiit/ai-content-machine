"""Daily Guide — render Mon-Sun ops guides."""

from datetime import date
from pathlib import Path

import streamlit as st


DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def render(REPO: Path):
    st.title("📅 Daily Guide")

    today_idx = date.today().weekday()
    today = DAYS[today_idx]

    tabs = st.tabs([d.title() for d in DAYS] + ["Operating Guide"])

    for i, day in enumerate(DAYS):
        with tabs[i]:
            mark = " (today)" if day == today else ""
            st.subheader(f"{day.title()}{mark}")
            md = REPO / "docs" / f"{day}.md"
            if md.exists():
                st.markdown(md.read_text())
            else:
                st.warning(f"`docs/{day}.md` missing")

    with tabs[7]:
        st.subheader("Weekly Operating Guide")
        guide = REPO / "docs" / "weekly-operating-guide.md"
        if guide.exists():
            st.markdown(guide.read_text())
