"""Render an HTML file to PDF.

Primary path: system headless Chrome `--print-to-pdf` (the exact method used to
render the W27 worksheet; guaranteed on macOS, honours `@page { size: A4 landscape }`
and prints backgrounds). Fallback: Playwright Chromium if a system browser is not
found. No external Python deps required for the primary path.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

# Common macOS / Linux Chrome-family binary locations, in preference order.
_CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
]
_CHROME_ON_PATH = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]


def _find_chrome() -> str | None:
    for p in _CHROME_CANDIDATES:
        if Path(p).is_file():
            return p
    for name in _CHROME_ON_PATH:
        found = shutil.which(name)
        if found:
            return found
    return None


def _render_with_chrome(chrome: str, html_path: Path, pdf_path: Path, timeout: int) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            chrome,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path.resolve().as_uri(),
        ],
        check=True,
        timeout=timeout,
        capture_output=True,
    )


def _render_with_playwright(html_path: Path, pdf_path: Path) -> None:
    from playwright.sync_api import sync_playwright

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
        page.wait_for_timeout(500)  # let webfonts settle
        page.pdf(
            path=str(pdf_path),
            prefer_css_page_size=True,  # honour @page size: A4 landscape
            print_background=True,      # render the dark header
        )
        browser.close()


def html_to_pdf(html_path: str | Path, pdf_path: str | Path, timeout: int = 60) -> Path:
    """Render `html_path` → `pdf_path`. Returns the PDF path.

    Tries system Chrome first, then Playwright. Raises RuntimeError if neither works.
    """
    html_path = Path(html_path)
    pdf_path = Path(pdf_path)
    if not html_path.is_file():
        raise FileNotFoundError(f"HTML not found: {html_path}")

    chrome = _find_chrome()
    if chrome:
        try:
            _render_with_chrome(chrome, html_path, pdf_path, timeout)
            return pdf_path
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            last_err: Exception = exc
    else:
        last_err = RuntimeError("no system Chrome found")

    try:
        _render_with_playwright(html_path, pdf_path)
        return pdf_path
    except Exception as exc:  # noqa: BLE001 — surface a combined failure
        raise RuntimeError(
            f"HTML→PDF render failed. Chrome: {last_err}. Playwright: {exc}"
        ) from exc
