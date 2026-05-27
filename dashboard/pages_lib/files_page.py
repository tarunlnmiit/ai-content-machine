"""Files — browse + preview repo files."""

from pathlib import Path

import streamlit as st


CATEGORIES = {
    "Blogs": ("content/blogs", "*.md"),
    "YT Scripts": ("content/scripts", "*_yt.md"),
    "Production Guides": ("content/scripts", "*_PRODUCTION_GUIDE.md"),
    "Captions (SRT)": ("content/scripts", "*.srt"),
    "Derivatives": ("content/derivatives", "*"),
    "Edited Videos": ("assets/video/edited", "*.mp4"),
    "Shorts": ("assets/video/edited/shorts", "*.mp4"),
    "Raw Videos": ("assets/raw", "*"),
    "Audio": ("assets/audio", "*"),
    "Thumbnails": ("assets/thumbnails", "*"),
    "Social Posts": ("assets/social_posts", "*"),
    "Reels": ("assets/reels", "*"),
    "Slides": ("assets/slides", "*"),
    "Output Scheduled": ("output/scheduled", "*"),
    "Ideas JSON": ("data/ideas", "*.json"),
    "Knowledge Base": ("data/kb", "*"),
    "Analytics": ("data/analytics", "*"),
}


def render(REPO: Path):
    st.title("📂 Files")

    cat = st.selectbox("Category", list(CATEGORIES.keys()))
    sub, pat = CATEGORIES[cat]
    base = REPO / sub
    if not base.exists():
        st.warning(f"Missing: `{sub}`")
        return

    files = sorted(base.rglob(pat) if pat == "*" else base.glob(pat),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    files = [f for f in files if f.is_file()]

    st.caption(f"`{sub}` — {len(files)} files")
    if not files:
        st.info("Empty.")
        return

    search = st.text_input("Filter", placeholder="substring...")
    if search:
        files = [f for f in files if search.lower() in f.name.lower()]

    sel = st.selectbox("File", files, format_func=lambda p: f"{p.relative_to(REPO)}  ({p.stat().st_size//1024} KB)")

    if not sel:
        return

    st.divider()
    col1, col2 = st.columns([3, 1])
    with col1:
        st.code(str(sel.relative_to(REPO)), language=None)
    with col2:
        with open(sel, "rb") as f:
            st.download_button("⬇ Download", f.read(), file_name=sel.name, use_container_width=True)

    suffix = sel.suffix.lower()
    if suffix in (".md", ".txt", ".srt", ".json", ".py", ".sh", ".csv"):
        text = sel.read_text(errors="ignore")
        if suffix == ".md":
            st.markdown(text)
            with st.expander("Raw markdown"):
                st.code(text, language="markdown")
        elif suffix == ".json":
            st.json(text if len(text) > 100000 else __import__("json").loads(text))
        else:
            st.code(text, language=suffix.lstrip("."))
    elif suffix in (".png", ".jpg", ".jpeg", ".webp"):
        st.image(str(sel))
    elif suffix in (".mp4", ".mov", ".webm"):
        st.video(str(sel))
    elif suffix in (".wav", ".mp3", ".m4a"):
        st.audio(str(sel))
    elif suffix == ".pdf":
        st.info("PDF preview not supported inline. Download to view.")
    else:
        st.info(f"Preview not supported for `{suffix}`.")
