"""Slugs — find + copy slugs from existing content."""

import re
from pathlib import Path

import streamlit as st


def _extract_slugs(REPO: Path) -> dict:
    """Return {slug: {paths: [...], type: 'blog'|'script'|'video'}}."""
    slugs = {}
    for f in (REPO / "content" / "blogs").glob("*.md") if (REPO/"content"/"blogs").exists() else []:
        slug = f.stem
        slugs.setdefault(slug, {"type": "blog", "paths": []})["paths"].append(str(f.relative_to(REPO)))
    for f in (REPO / "content" / "scripts").glob("*_yt.md") if (REPO/"content"/"scripts").exists() else []:
        slug = f.stem.replace("_yt", "")
        slugs.setdefault(slug, {"type": "script", "paths": []})["paths"].append(str(f.relative_to(REPO)))
    for f in (REPO / "assets" / "video" / "edited").glob("*.mp4") if (REPO/"assets"/"video"/"edited").exists() else []:
        slug = f.stem
        slugs.setdefault(slug, {"type": "video", "paths": []})["paths"].append(str(f.relative_to(REPO)))
    return slugs


def render(REPO: Path):
    st.title("🔗 Slugs")
    st.caption("Browse and copy slugs from existing content. Click a slug to copy.")

    slugs = _extract_slugs(REPO)
    if not slugs:
        st.info("No slugs found yet.")
        return

    search = st.text_input("Filter", placeholder="ds, life, poetry, date...")
    items = sorted(slugs.items(), key=lambda x: x[0], reverse=True)
    if search:
        items = [(s, d) for s, d in items if search.lower() in s.lower()]

    st.caption(f"{len(items)} slugs")

    for slug, data in items[:60]:
        with st.container(border=True):
            c1, c2, c3 = st.columns([4, 2, 1])
            with c1:
                st.code(slug, language=None)
                st.caption(" · ".join(data["paths"]))
            with c2:
                st.write(f"**{data['type']}**")
            with c3:
                if st.button("Use", key=f"use_{slug}"):
                    st.session_state["last_slug"] = slug
                    st.toast(f"Stored slug: {slug[:40]}")
