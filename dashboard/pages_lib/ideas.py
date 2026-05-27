"""Ideas — browse weekly_ideas.md + push to Notion."""

import re
from pathlib import Path

import streamlit as st

from ._common import py_cmd, run_cmd, show_run_result


def _parse_ideas(md: str) -> dict:
    out = {}
    cur_niche = None
    cur_title = None
    cur_meta = {}
    for line in md.splitlines():
        line = line.rstrip()
        if line.startswith("## "):
            cur_niche = line[3:].strip()
            out[cur_niche] = []
        m = re.match(r"^### \d+\.\s+(.*)", line)
        if m:
            if cur_title:
                out[cur_niche].append({"title": cur_title, **cur_meta})
            cur_title = m.group(1).strip()
            cur_meta = {}
            continue
        m = re.match(r"^- \*\*(\w+):\*\*\s*(.*)", line)
        if m:
            cur_meta[m.group(1).lower()] = m.group(2).strip()
    if cur_title and cur_niche:
        out[cur_niche].append({"title": cur_title, **cur_meta})
    return out


def render(REPO: Path):
    st.title("💡 Ideas")

    ideas_md = REPO / "data" / "ideas" / "weekly_ideas.md"
    if not ideas_md.exists():
        st.warning("No `weekly_ideas.md` yet. Run daily_ideas pipeline.")
        if st.button("Run daily_ideas.sh now"):
            res = run_cmd(["bash", "scripts/daily_ideas.sh"], cwd=REPO, timeout=600)
            show_run_result(res, "daily_ideas.sh")
            st.rerun()
        return

    grouped = _parse_ideas(ideas_md.read_text())

    cols = st.columns(3)
    niches = list(grouped.keys())
    for i, niche in enumerate(niches[:3]):
        with cols[i]:
            st.subheader(niche)
            for item in grouped[niche]:
                with st.container(border=True):
                    st.markdown(f"**{item['title']}**")
                    meta_bits = []
                    if "score" in item:
                        meta_bits.append(f"score `{item['score']}`")
                    if "source" in item:
                        meta_bits.append(f"src `{item['source']}`")
                    st.caption(" · ".join(meta_bits))
                    if item.get("url"):
                        st.link_button("Open source", item["url"], use_container_width=True)
                    b1, b2 = st.columns(2)
                    if b1.button("Pick", key=f"pick_{niche}_{item['title'][:30]}", use_container_width=True):
                        st.session_state["picked_topic"] = item["title"]
                        st.session_state["picked_niche"] = niche
                        st.toast(f"Picked: {item['title'][:50]}")
                    if b2.button("Skip", key=f"skip_{niche}_{item['title'][:30]}", use_container_width=True):
                        pass

    st.divider()
    if "picked_topic" in st.session_state:
        st.success(f"**Picked:** {st.session_state['picked_topic']}  ·  niche: `{st.session_state.get('picked_niche')}`")
        c1, c2, c3 = st.columns(3)
        if c1.button("→ Produce blog", use_container_width=True):
            st.session_state["nav_target"] = "workflows"
            st.session_state["preselect_workflow"] = "produce_blog"
            st.rerun()
        if c2.button("→ Ghostwrite from notes", use_container_width=True):
            st.session_state["nav_target"] = "workflows"
            st.session_state["preselect_workflow"] = "ghostwrite"
            st.rerun()
        if c3.button("Clear pick", use_container_width=True):
            st.session_state.pop("picked_topic", None)
            st.session_state.pop("picked_niche", None)
            st.rerun()

    st.divider()
    st.subheader("Notion sync")
    c1, c2 = st.columns(2)
    if c1.button("Dry-run sync", use_container_width=True):
        res = run_cmd(py_cmd("scripts/sync_ideas_to_notion.py", "--dry-run"), cwd=REPO, timeout=60)
        show_run_result(res, "Dry-run")
    if c2.button("Real sync → Notion", type="primary", use_container_width=True):
        res = run_cmd(py_cmd("scripts/sync_ideas_to_notion.py"), cwd=REPO, timeout=120)
        show_run_result(res, "Notion sync")

    st.divider()
    st.subheader("Refresh sources")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("Reddit", use_container_width=True):
        res = run_cmd(py_cmd("scripts/rss_scraper.py"), cwd=REPO, timeout=300)
        show_run_result(res, "rss_scraper.py")
    if c2.button("External (HN/arXiv/etc)", use_container_width=True):
        res = run_cmd(py_cmd("scripts/fetch_external_feeds.py"), cwd=REPO, timeout=300)
        show_run_result(res, "fetch_external_feeds.py")
    if c3.button("Google Suggest", use_container_width=True):
        res = run_cmd(py_cmd("scripts/fetch_google_suggest.py", "--quick"), cwd=REPO, timeout=300)
        show_run_result(res, "fetch_google_suggest.py")
    if c4.button("Rescore", use_container_width=True):
        res = run_cmd(py_cmd("scripts/idea_scorer.py", "--top", "5"), cwd=REPO, timeout=120)
        show_run_result(res, "idea_scorer.py")
