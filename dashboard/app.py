#!/usr/bin/env python3
"""Content Machine — operator dashboard.

Run:
  bash dashboard/run.sh
  # or:
  streamlit run dashboard/app.py
"""

import os
import subprocess
import sys
from pathlib import Path

import streamlit as st

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

st.set_page_config(
    page_title="Content Machine",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Sidebar nav
PAGES = {
    "🏠 Home": "home",
    "💡 Ideas": "ideas",
    "📅 Daily Guide": "daily_guide",
    "🗓️ Posting Schedule": "posting_schedule",
    "⚙️ Workflows": "workflows",
    "📂 Files": "files",
    "⬆️ Upload": "upload",
    "📋 Checklist": "checklist",
    "🏷️ Medium Tags": "medium_tags",
    "🔗 Slugs": "slugs",
    "📊 Logs": "logs",
    "🩺 System": "system",
}

st.sidebar.title("🎬 Content Machine")
choice = st.sidebar.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")
page = PAGES[choice]

st.sidebar.markdown("---")
st.sidebar.caption(f"Repo: `{REPO.name}`")
st.sidebar.caption(f"Branch: `{subprocess.run(['git','-C',str(REPO),'branch','--show-current'], capture_output=True, text=True).stdout.strip() or 'detached'}`")


# ── Page modules ────────────────────────────────────────────────────────
if page == "home":
    from pages_lib import home
    home.render(REPO)
elif page == "ideas":
    from pages_lib import ideas
    ideas.render(REPO)
elif page == "daily_guide":
    from pages_lib import daily_guide
    daily_guide.render(REPO)
elif page == "workflows":
    from pages_lib import workflows
    workflows.render(REPO)
elif page == "files":
    from pages_lib import files_page
    files_page.render(REPO)
elif page == "upload":
    from pages_lib import upload
    upload.render(REPO)
elif page == "checklist":
    from pages_lib import publishing_checklist
    publishing_checklist.render(REPO)
elif page == "slugs":
    from pages_lib import slugs
    slugs.render(REPO)
elif page == "logs":
    from pages_lib import logs
    logs.render(REPO)
elif page == "system":
    from pages_lib import system
    system.render(REPO)
elif page == "posting_schedule":
    from pages_lib import posting_schedule
    posting_schedule.render(REPO)
elif page == "medium_tags":
    from pages_lib import medium_tags
    medium_tags.render(REPO)
