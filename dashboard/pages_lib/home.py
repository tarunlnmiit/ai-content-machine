"""Home — status overview."""

import subprocess
from datetime import datetime
from pathlib import Path

import streamlit as st


def _launchd_status(label: str) -> str:
    res = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
    for line in res.stdout.splitlines():
        if label in line:
            parts = line.split("\t")
            pid = parts[0] if parts else "?"
            return f"PID {pid}" if pid not in ("-", "") else "loaded (idle)"
    return "not loaded"


def _file_age(p: Path) -> str:
    if not p.exists():
        return "missing"
    age_h = (datetime.now().timestamp() - p.stat().st_mtime) / 3600
    if age_h < 1:
        return f"{int(age_h*60)} min ago"
    if age_h < 24:
        return f"{age_h:.1f} h ago"
    return f"{age_h/24:.1f} days ago"


def render(REPO: Path):
    st.title("🏠 Home")
    st.caption(f"`{REPO}`")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Automation")
        st.metric("Daily Ideas", _launchd_status("dailyideas"))
        st.metric("Scheduler", _launchd_status("scheduler"))
        st.metric("KB Build", _launchd_status("buildkb"))

    with col2:
        st.subheader("Fresh data")
        st.metric("weekly_ideas.md", _file_age(REPO / "data" / "ideas" / "weekly_ideas.md"))
        st.metric("master_brief.md", _file_age(REPO / "data" / "kb" / "master_brief.md"))
        st.metric("scheduling.db", _file_age(REPO / "data" / "scheduling.db"))

    with col3:
        st.subheader("Recent counts")
        blogs = list((REPO / "content" / "blogs").glob("*.md")) if (REPO/"content"/"blogs").exists() else []
        scripts = list((REPO / "content" / "scripts").glob("*_yt.md")) if (REPO/"content"/"scripts").exists() else []
        edited = list((REPO / "assets" / "video" / "edited").glob("*.mp4")) if (REPO/"assets"/"video"/"edited").exists() else []
        st.metric("Blogs", len(blogs))
        st.metric("YT scripts", len(scripts))
        st.metric("Edited videos", len(edited))

    st.divider()

    st.subheader("Quick actions")
    a, b, c, d = st.columns(4)
    if a.button("🔄 Refresh ideas now", use_container_width=True):
        st.session_state["nav_target"] = "workflows"
        st.session_state["preselect_workflow"] = "daily_ideas"
        st.rerun()
    if b.button("📝 Pick topic (Monday)", use_container_width=True):
        st.session_state["nav_target"] = "ideas"
        st.rerun()
    if c.button("📅 Today's guide", use_container_width=True):
        st.session_state["nav_target"] = "daily_guide"
        st.rerun()
    if d.button("📊 Tail logs", use_container_width=True):
        st.session_state["nav_target"] = "logs"
        st.rerun()

    st.divider()
    st.subheader("Recent activity")
    log = REPO / "data" / "analytics" / "scheduler.log"
    if log.exists():
        with st.expander("scheduler.log — last 20 lines"):
            st.code("\n".join(log.read_text().splitlines()[-20:]), language="text")

    daily_log = Path("/tmp/daily_ideas.log")
    if daily_log.exists():
        with st.expander("daily_ideas.log — last 30 lines"):
            st.code("\n".join(daily_log.read_text().splitlines()[-30:]), language="text")
