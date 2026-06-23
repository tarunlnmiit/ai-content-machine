"""Shared dashboard utilities."""

import subprocess
import time
from pathlib import Path

import streamlit as st


def run_cmd(cmd: list, cwd: Path, timeout: int = 300) -> dict:
    """Run command, return {ok, stdout, stderr, code, elapsed}."""
    t0 = time.time()
    try:
        res = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
        return {
            "ok": res.returncode == 0,
            "stdout": res.stdout,
            "stderr": res.stderr,
            "code": res.returncode,
            "elapsed": time.time() - t0,
        }
    except subprocess.TimeoutExpired:
        return {"ok": False, "stdout": "", "stderr": f"timeout after {timeout}s", "code": -1, "elapsed": timeout}
    except FileNotFoundError as e:
        return {"ok": False, "stdout": "", "stderr": str(e), "code": -1, "elapsed": 0}


def show_run_result(result: dict, label: str = ""):
    if label:
        st.write(f"**{label}** — {result['elapsed']:.1f}s")
    if result["ok"]:
        st.success(f"✓ exit {result['code']}")
    else:
        st.error(f"✗ exit {result['code']}")
    if result["stdout"]:
        with st.expander("stdout", expanded=False):
            st.code(result["stdout"][-4000:], language="text")
    if result["stderr"]:
        with st.expander("stderr", expanded=not result["ok"]):
            st.code(result["stderr"][-4000:], language="text")


CONDA_PY = "/Users/tarungupta/miniconda3/envs/content_engine_env/bin/python3.14"


def py_cmd(script: str, *args: str) -> list:
    """Build [python, script.py, args...] using conda env python."""
    py = CONDA_PY if Path(CONDA_PY).exists() else "python3"
    return [py, script, *args]


def copy_button(text: str, label: str = "Copy", key: str = None):
    """Render a text + copy-on-click (uses JS via components)."""
    col1, col2 = st.columns([5, 1])
    with col1:
        st.code(text, language=None)
    with col2:
        st.button(label, key=key or text[:30], help="Click to select code on left, then ⌘C")


NICHES = ["ds", "life", "poetry"]
NICHE_LABELS = {"ds": "Data Science / Tech", "life": "Life & Self-Dev", "poetry": "Poetry / Quotes"}
