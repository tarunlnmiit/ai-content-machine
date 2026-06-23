"""Upload — drop files to known repo dirs."""

from pathlib import Path

import streamlit as st


TARGETS = {
    "Raw camera video → assets/raw/": "assets/raw",
    "Voiceover audio → assets/audio/": "assets/audio",
    "Thumbnail image → assets/thumbnails/": "assets/thumbnails",
    "Notes/transcript → data/poems/ or content/scripts/": "content/scripts",
    "Poem text → data/poems/": "data/poems",
    "Custom path...": None,
}


def render(REPO: Path):
    st.title("⬆️ Upload Files")

    target_label = st.selectbox("Destination", list(TARGETS.keys()))
    target = TARGETS[target_label]
    if target is None:
        target = st.text_input("Custom subdir under repo root", value="assets/raw")

    rename = st.text_input("Rename to (optional, blank = keep original name)", value="")

    files = st.file_uploader("Drop files", accept_multiple_files=True)
    if files and st.button("Save", type="primary"):
        dst = REPO / target
        dst.mkdir(parents=True, exist_ok=True)
        for f in files:
            name = rename or f.name
            (dst / name).write_bytes(f.getbuffer())
            st.success(f"✓ {dst / name}")
        st.toast(f"Saved {len(files)} file(s)")
