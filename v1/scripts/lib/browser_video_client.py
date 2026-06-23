#!/usr/bin/env python3
"""Browser-based video generation via Playwright.

Four backends run in parallel — each gets its own prompt variant.
No fallback. All succeed or fail independently.

Backends:
  hf      — HuggingFace Space: Lightricks/LTX-2-3 (free, no auth)
  ltxio   — ltx.io (saved session)
  qwen    — qwen.ai Wan 2.1 (saved session, Alibaba account)
  hunyuan — hunyuanvideo.org (saved session, Tencent account)

Session setup (one-time per service):
  python3 scripts/lib/browser_video_client.py --save-session ltxio
  python3 scripts/lib/browser_video_client.py --save-session qwen
  python3 scripts/lib/browser_video_client.py --save-session hunyuan

Parallel generation:
  from lib.browser_video_client import generate_all_parallel
  results = asyncio.run(generate_all_parallel(tasks))
  # tasks = [{"backend": "hf", "prompt": "...", "output_path": Path(...), "duration_sec": 5}, ...]
"""

import argparse
import asyncio
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
SESSION_DIR = REPO / ".browser_sessions"

QWEN_SESSION  = SESSION_DIR / "qwen.json"

HF_SPACE_URL   = "https://huggingface.co/spaces/Lightricks/LTX-2-3"
QWEN_URL       = "https://chat.qwen.ai/"
QWEN_VIDEO_URL = "https://chat.qwen.ai/"
HUNYUAN_URL    = "https://www.hunyuanvideo.org/en/create"

HEADLESS = os.environ.get("BROWSER_HEADLESS", "1") == "1"
GENERATE_TIMEOUT_MS = 180_000  # 3 min per generation

STEALTH_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
STEALTH_JS = "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"


# ---------------------------------------------------------------------------
# Browser helpers
# ---------------------------------------------------------------------------

async def _stealth_browser(p, headless: bool = True):
    args = ["--disable-blink-features=AutomationControlled", "--disable-infobars"]
    try:
        return await p.chromium.launch(headless=headless, channel="chrome", args=args)
    except Exception:
        return await p.chromium.launch(headless=headless, args=args)


async def _stealth_context(browser, session_file: Path | None = None):
    ctx = await browser.new_context(
        user_agent=STEALTH_UA,
        accept_downloads=True,
        storage_state=str(session_file) if session_file and session_file.exists() else None,
    )
    await ctx.add_init_script(STEALTH_JS)
    return ctx


async def _download_via_js(page, video_src: str, output_path: Path) -> None:
    """Trigger browser download of video_src via injected anchor click."""
    async with page.expect_download(timeout=30_000) as dl_info:
        await page.evaluate(f"""
            const a = document.createElement('a');
            a.href = '{video_src}';
            a.download = 'video.mp4';
            document.body.appendChild(a);
            a.click();
        """)
    download = await dl_info.value
    await download.save_as(output_path)


async def _wait_and_download(page, output_path: Path) -> None:
    """Wait for Download button or video[src], then save to output_path."""
    try:
        async with page.expect_download(timeout=GENERATE_TIMEOUT_MS) as dl_info:
            dl_btn = page.locator("button").filter(has_text="Download").first
            await dl_btn.wait_for(state="visible", timeout=GENERATE_TIMEOUT_MS)
            await dl_btn.click()
        download = await dl_info.value
        await download.save_as(output_path)
    except Exception:
        video_el = page.locator("video[src]").first
        await video_el.wait_for(state="visible", timeout=GENERATE_TIMEOUT_MS)
        video_src = await video_el.get_attribute("src")
        if not video_src:
            raise RuntimeError("no video src found after generation")
        if video_src.startswith("/"):
            base = page.url.split("/")[0] + "//" + page.url.split("/")[2]
            video_src = base + video_src
        await _download_via_js(page, video_src, output_path)


async def _fill_and_submit(page, prompt: str) -> None:
    """Fill prompt field and click Generate (or press Enter)."""
    prompt_sel = "textarea, [contenteditable='true'], input[placeholder*='prompt' i], input[type='text']"
    await page.wait_for_selector(prompt_sel, timeout=30_000)
    prompt_el = page.locator(prompt_sel).first
    await prompt_el.click()
    await prompt_el.press_sequentially(prompt, delay=10)
    try:
        gen_btn = page.locator("button").filter(has_text="Generate").first
        await gen_btn.wait_for(state="visible", timeout=5_000)
        await gen_btn.click()
    except Exception:
        await prompt_el.press("Enter")


# ---------------------------------------------------------------------------
# Per-backend generators
# ---------------------------------------------------------------------------

async def _wait_for_page(page, timeout_ms: int = 60_000) -> None:
    """Wait for page to be interactive. Uses domcontentloaded + prompt element appears."""
    await page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
    # Give JS frameworks time to mount
    await page.wait_for_timeout(3_000)


async def _generate_hf(prompt: str, output_path: Path, duration_sec: int) -> None:
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await _stealth_browser(p, headless=HEADLESS)
        ctx = await browser.new_context(accept_downloads=True)
        await ctx.add_init_script(STEALTH_JS)
        page = await ctx.new_page()
        print(f"         [hf] loading space...")
        await page.goto(HF_SPACE_URL, timeout=60_000)
        await _wait_for_page(page, timeout_ms=90_000)

        # HF Space embeds the Gradio UI in an iframe
        frame = page.frame_locator("iframe").first
        print(f"         [hf] waiting for prompt field...")
        textarea = frame.locator("textarea").first
        await textarea.wait_for(state="visible", timeout=60_000)
        await textarea.click()
        await textarea.press_sequentially(prompt, delay=10)
        print(f"         [hf] prompt filled, generating...")

        try:
            dur = frame.locator("input[type='number']").first
            if await dur.is_visible(timeout=2_000):
                await dur.fill(str(min(duration_sec, 10)))
        except Exception:
            pass

        gen_btn = frame.locator("button").filter(has_text="Generate Video").first
        await gen_btn.wait_for(state="visible", timeout=10_000)
        await gen_btn.click()
        print(f"         [hf] queued, waiting for video...")

        video_el = frame.locator("video[src]").first
        await video_el.wait_for(state="visible", timeout=GENERATE_TIMEOUT_MS)
        video_src = await video_el.get_attribute("src")
        if not video_src:
            raise RuntimeError("[hf] no video src after generation")
        if video_src.startswith("/"):
            base = page.url.split("/")[0] + "//" + page.url.split("/")[2]
            video_src = base + video_src
        await _download_via_js(page, video_src, output_path)
        await browser.close()


async def _generate_ltxio(prompt: str, output_path: Path, duration_sec: int) -> None:
    # ltx.io/model/ltx-2-3 is a marketing page — no generation UI.
    # Backend removed; keeping stub so callers that specify --backend ltxio get a clear error.
    raise RuntimeError("ltxio backend removed: ltx.io has no generation UI. Use hf or hunyuan instead.")


async def _generate_qwen(prompt: str, output_path: Path, duration_sec: int) -> None:
    from playwright.async_api import async_playwright
    if not QWEN_SESSION.exists():
        raise RuntimeError("qwen session missing — run --save-session qwen")
    async with async_playwright() as p:
        browser = await _stealth_browser(p, headless=HEADLESS)
        ctx = await _stealth_context(browser, session_file=QWEN_SESSION)
        page = await ctx.new_page()
        print(f"         [qwen] loading...")
        await page.goto(QWEN_VIDEO_URL, timeout=60_000)
        await _wait_for_page(page)
        print(f"         [qwen] filling prompt...")
        await _fill_and_submit(page, prompt)
        print(f"         [qwen] generating...")
        await _wait_and_download(page, output_path)
        await browser.close()


async def _generate_hunyuan(prompt: str, output_path: Path, duration_sec: int) -> None:
    # hunyuanvideo.org is a free third-party aggregator — no login required.
    # UI is inside an iframe. Uses "Wan 2.2 Fast" model for variety vs HF's LTX-2.3.
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await _stealth_browser(p, headless=HEADLESS)
        ctx = await _stealth_context(browser)
        page = await ctx.new_page()
        print(f"         [hunyuan] loading...")
        await page.goto(HUNYUAN_URL, timeout=60_000)
        await _wait_for_page(page, timeout_ms=90_000)

        # Generation UI is inside the iframe in <main>, not the ad iframes
        frame = page.frame_locator("main iframe").first
        print(f"         [hunyuan] waiting for UI...")

        # Select Wan 2.2 Fast for variety (HF Space already uses LTX-2.3)
        try:
            model_select = frame.locator("select").first
            await model_select.wait_for(state="visible", timeout=15_000)
            await model_select.select_option(label="Wan 2.2 Fast (⚡ Fast · T2V+I2V)")
        except Exception:
            pass  # Keep default model if selector not found

        # Set aspect ratio 16:9 (div with cursor, not a button)
        try:
            ratio_btn = frame.locator("text=16:9").first
            if await ratio_btn.is_visible(timeout=3_000):
                await ratio_btn.click()
        except Exception:
            pass

        print(f"         [hunyuan] filling prompt...")
        prompt_el = frame.get_by_role("textbox").first
        await prompt_el.wait_for(state="visible", timeout=30_000)
        await prompt_el.click()
        await prompt_el.press_sequentially(prompt, delay=10)

        gen_btn = frame.locator("button").filter(has_text="Generate Video").first
        await gen_btn.wait_for(state="visible", timeout=10_000)
        await gen_btn.click()
        print(f"         [hunyuan] generating...")

        video_el = frame.locator("video[src]").first
        await video_el.wait_for(state="visible", timeout=GENERATE_TIMEOUT_MS)
        video_src = await video_el.get_attribute("src")
        if not video_src:
            raise RuntimeError("[hunyuan] no video src after generation")
        if video_src.startswith("/"):
            base = page.url.split("/")[0] + "//" + page.url.split("/")[2]
            video_src = base + video_src
        await _download_via_js(page, video_src, output_path)
        await browser.close()


_BACKEND_FN = {
    "hf":      _generate_hf,
    "ltxio":   _generate_ltxio,
    "qwen":    _generate_qwen,
    "hunyuan": _generate_hunyuan,
}


# ---------------------------------------------------------------------------
# Parallel runner
# ---------------------------------------------------------------------------

async def _run_one(task: dict) -> dict:
    """Run single backend task. Returns result dict with success/error."""
    backend = task["backend"]
    prompt  = task["prompt"]
    out     = task["output_path"]
    dur     = task.get("duration_sec", 5)

    fn = _BACKEND_FN.get(backend)
    if fn is None:
        return {**task, "success": False, "error": f"unknown backend: {backend}"}
    try:
        await fn(prompt, out, dur)
        print(f"         [{backend}] ✓ → {out.name}")
        return {**task, "success": True, "error": None}
    except Exception as e:
        print(f"         [{backend}] ✗ {e}")
        return {**task, "success": False, "error": str(e)}


async def generate_all_parallel(tasks: list[dict]) -> list[dict]:
    """
    Fire all tasks concurrently. Each task: {backend, prompt, output_path, duration_sec}.
    Returns list of results with success/error per task.
    """
    return await asyncio.gather(*[_run_one(t) for t in tasks])


async def generate_worker_pool(
    cue_tasks: list[dict],
    backends: list[str],
) -> list[dict]:
    """
    Worker pool: N backends = N workers. Each worker pulls next cue when free.
    One video per cue (not one per backend). Maximises throughput without explosion.

    cue_tasks: [{prompt, output_path, duration_sec, ...}] — no backend key needed.
    Returns list of result dicts with backend, success, error added.
    """
    queue: asyncio.Queue = asyncio.Queue()
    for task in cue_tasks:
        await queue.put(task)

    results: list[dict] = []

    async def worker(backend: str) -> None:
        while True:
            try:
                task = queue.get_nowait()
            except asyncio.QueueEmpty:
                return
            result = await _run_one({**task, "backend": backend})
            results.append(result)
            queue.task_done()

    await asyncio.gather(*[worker(b) for b in backends])
    return results


def skipped_backends() -> set[str]:
    """Backends disabled via SKIP_BACKENDS env var (comma-separated)."""
    raw = os.environ.get("SKIP_BACKENDS", "qwen")  # qwen disabled until network fixed
    return {b.strip() for b in raw.split(",") if b.strip()}


def active_backends() -> list[str]:
    """Return backends that are ready (have session or need none) and not skipped."""
    skip = skipped_backends()
    backends = ["hf", "hunyuan"]  # always available — no login required
    if QWEN_SESSION.exists():
        backends.append("qwen")
    return [b for b in backends if b not in skip]


# ---------------------------------------------------------------------------
# Session management
# ---------------------------------------------------------------------------

async def save_session(service: str) -> None:
    from playwright.async_api import async_playwright
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    targets = {
        "qwen": (QWEN_URL, QWEN_SESSION),
    }
    if service not in targets:
        raise ValueError(f"Unknown service: {service}. Choose: {list(targets)}")
    url, session_file = targets[service]
    print(f"Opening {service} ({url}) — log in, then press Enter here.")
    async with async_playwright() as p:
        browser = await _stealth_browser(p, headless=False)
        ctx = await _stealth_context(browser)
        page = await ctx.new_page()
        await page.goto(url)
        print(f"Browser open. Finish login, then press Enter...")
        input()
        await ctx.storage_state(path=str(session_file))
        await browser.close()
    print(f"Session saved → {session_file}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--save-session", choices=["qwen"],
                        help="Interactive: save login session (qwen only — hf and hunyuan need no login)")
    parser.add_argument("--active", action="store_true",
                        help="List active backends")
    parser.add_argument("--test", help="Test prompt (fires all active backends in parallel)")
    parser.add_argument("--output-dir", default="/tmp", help="Output directory for --test")
    args = parser.parse_args()

    if args.save_session:
        asyncio.run(save_session(args.save_session))
    elif args.active:
        print("Active backends:", active_backends())
    elif args.test:
        backends = active_backends()
        print(f"Firing {len(backends)} backends in parallel: {backends}")
        tasks = [
            {
                "backend": b,
                "prompt": args.test,
                "output_path": Path(args.output_dir) / f"test_{b}.mp4",
                "duration_sec": 5,
            }
            for b in backends
        ]
        results = asyncio.run(generate_all_parallel(tasks))
        for r in results:
            status = "✓" if r["success"] else f"✗ {r['error']}"
            print(f"  [{r['backend']}] {status}")
    else:
        parser.print_help()
