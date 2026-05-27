"""System — launchd + scheduler + env status."""

import json
import os
import sqlite3
import subprocess
from pathlib import Path

import streamlit as st


def _launchctl_list() -> list:
    res = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
    rows = []
    for line in res.stdout.splitlines():
        if "contentmachine" in line:
            parts = line.split("\t")
            rows.append({"PID": parts[0], "Exit": parts[1], "Label": parts[2] if len(parts) > 2 else ""})
    return rows


def _env_check(REPO: Path) -> dict:
    env_file = REPO / ".env"
    keys = []
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                keys.append(line.split("=", 1)[0])
    return {"file_exists": env_file.exists(), "key_count": len(keys), "keys": keys}


def _db_stats(db_path: Path) -> dict:
    if not db_path.exists():
        return {"exists": False}
    try:
        con = sqlite3.connect(str(db_path))
        cur = con.cursor()
        tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
        counts = {}
        for t in tables:
            try:
                counts[t] = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            except Exception:
                counts[t] = "?"
        return {"exists": True, "tables": counts}
    finally:
        con.close()


def render(REPO: Path):
    st.title("🩺 System")

    st.subheader("launchd agents (com.contentmachine.*)")
    rows = _launchctl_list()
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.warning("No content-machine agents loaded.")

    st.divider()
    st.subheader("Environment")
    env = _env_check(REPO)
    c1, c2 = st.columns(2)
    c1.metric(".env file", "found" if env["file_exists"] else "missing")
    c2.metric("keys", env["key_count"])
    with st.expander("Keys (names only)"):
        st.code("\n".join(env["keys"]) or "(none)", language="text")

    st.divider()
    st.subheader("scheduling.db")
    stats = _db_stats(REPO / "data" / "scheduling.db")
    if stats.get("exists"):
        st.json(stats["tables"])
    else:
        st.info("DB missing.")

    st.divider()
    st.subheader("Disk usage")
    for sub in ["assets", "content", "data", "graphify-out", "dashboard"]:
        p = REPO / sub
        if not p.exists():
            continue
        size = sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
        st.write(f"`{sub}` — {size/1024/1024:.1f} MB")

    st.divider()
    st.subheader("Claude CLI cache")
    cache = REPO / ".cache" / "claude"
    if cache.exists():
        files = list(cache.glob("*.txt"))
        c1, c2, c3 = st.columns(3)
        c1.metric("entries", len(files))
        c2.metric("size", f"{sum(f.stat().st_size for f in files)/1024:.1f} KB")
        if c3.button("🗑 Bust cache"):
            for f in files:
                f.unlink()
            st.toast(f"Removed {len(files)} entries")
            st.rerun()
    else:
        st.info("No cache yet.")
