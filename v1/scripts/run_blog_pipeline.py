#!/usr/bin/env python3
"""One command: blog → ALL text + social + media derivatives (videos excluded).

Run this once a blog exists (or let it generate the blog from a topic) and it produces every
non-video derivative automatically: text posts, social images + carousel, slide deck, IG reel
brief, thumbnail brief, worksheet outline, then stages everything to the scheduler.

VIDEOS are intentionally out of scope — long-form + shorts need a recorded voiceover and stay in
`run_voiceover_week.py`.

Modes:
  # existing blog
  python3 scripts/run_blog_pipeline.py --input content/blogs/2026-W22/<slug>.md
  # generate the blog first, then everything
  python3 scripts/run_blog_pipeline.py --topic "Why X beats Y" --niche ds

Idempotent: each step skips when its output exists; --force redoes all.
"""

import argparse
import glob
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO = Path(__file__).parent.parent
SCRIPTS = REPO / "scripts"
sys.path.insert(0, str(SCRIPTS))

from lib.schedule_calc import get_iso_week
from lib.content_paths import derivatives_dir
from lib.notify import notify
from lib.seo import extract_seo, seo_manual_steps

NICHE_FULL = {"ds": "data_science_tech", "life": "life_self_dev", "poetry": "poetry_quotes"}

_T0 = time.time()


def step(label: str) -> None:
    print(f"\n{'━' * 64}\n▶ {label}   (+{time.time() - _T0:.0f}s)\n{'━' * 64}", flush=True)


def run(cmd: list, dry: bool) -> bool:
    printable = " ".join(str(c) for c in cmd)
    print(f"\n$ {printable}")
    if dry:
        return True
    r = subprocess.run([str(c) for c in cmd])
    if r.returncode != 0:
        print(f"  [FAIL] exit {r.returncode}: {printable[:80]}", file=sys.stderr)
        return False
    return True


def niche_from_slug(slug: str) -> str:
    if "data_science_tech" in slug:
        return "ds"
    if "poetry_quotes" in slug:
        return "poetry"
    return "life"


def produce_blog(args) -> Path:
    """Topic mode: generate the blog, then return its path (newest matching niche this week)."""
    cmd = ["python3", SCRIPTS / "produce_blog.py", "--topic", args.topic, "--niche", args.niche]
    if args.humanize:
        cmd.append("--humanize")
    if args.listicle:
        cmd += ["--listicle", str(args.listicle)]
    if args.project:
        cmd += ["--project", args.project]
    if not run(cmd, args.dry_run):
        sys.exit("produce_blog failed")
    if args.dry_run:
        return REPO / "content" / "blogs" / "DRYRUN" / f"DRYRUN_{NICHE_FULL[args.niche]}_topic.md"
    blogs = sorted(
        REPO.glob(f"content/blogs/*/*{NICHE_FULL[args.niche]}*.md"),
        key=lambda p: p.stat().st_mtime,
    )
    if not blogs:
        sys.exit("produce_blog ran but no blog file found")
    return blogs[-1]


def main() -> None:
    ap = argparse.ArgumentParser(description="Blog → all derivatives + media (videos excluded)")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--input", help="Path to an existing blog .md")
    src.add_argument("--topic", help="Topic — generates the blog first (requires --niche)")
    ap.add_argument("--niche", choices=["ds", "life", "poetry"], help="Required with --topic")
    ap.add_argument("--project", default=None, help="Build-in-public project key")
    ap.add_argument("--humanize", action="store_true", help="produce_blog humanize pass (topic mode)")
    ap.add_argument("--listicle", type=int, default=None, help="produce_blog listicle N (topic mode)")
    ap.add_argument("--force", action="store_true", help="Redo every step even if output exists")
    ap.add_argument("--no-stage", action="store_true", help="Skip load_posts staging")
    ap.add_argument("--skip-thumbnail", action="store_true", help="Skip the HTML thumbnail render")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.topic and not args.niche:
        ap.error("--topic requires --niche")

    dry = args.dry_run
    force = args.force
    force_flag = ["--force"] if force else []
    proj_flag = ["--project", args.project] if args.project else []

    # ── Resolve blog ───────────────────────────────────────────────
    if args.topic:
        step("[0] Produce blog (topic mode)")
        blog = produce_blog(args)
    else:
        blog = Path(args.input)
        if not blog.is_absolute():
            blog = REPO / blog
        if not blog.exists() and not dry:
            sys.exit(f"ERROR: blog not found: {blog}")

    slug = blog.stem
    date = slug[:10]
    week = get_iso_week(date)
    niche = niche_from_slug(slug)
    ddir = derivatives_dir(date, slug)
    print(f"\n=== Blog pipeline: {slug}  (niche={niche}, week={week}) ===")

    def skip(label: str, exists: bool) -> bool:
        if exists and not force:
            print(f"  [skip] {label} (exists; --force to redo)")
            return True
        return False

    results: dict[str, bool] = {}

    # ── 1. Text derivatives (one call writes the full set) ─────────
    # Stays FIRST and sequential — every derivative below consumes its output.
    step("[1/7] Text derivatives (LinkedIn/IG/Threads/newsletter/polls/YT meta/schedule)")
    if not skip("text derivatives", (ddir / "linkedin_post.txt").exists()):
        results["text derivatives"] = run(
            ["python3", SCRIPTS / "repurpose_blog.py", "--input", str(blog)] + proj_flag, dry)

    # ── 2-6. Independent derivative stages (parallel) ──────────────
    # Each stage reads only the blog + repurpose_blog output — none reads another
    # stage's output. 3 workers: parallel `claude -p` sessions stay within Max 5x
    # limits (same convention as generate_buffer.py).

    def stage_social_images() -> bool:
        # Carousel HTML is produced inside Phase 2 of repurpose_blog.py (step 1/7 above).
        step("[2/7] Social images (Instagram/LinkedIn/Threads PNGs)")
        social_png = REPO / "assets" / "social_posts" / week / f"{slug}_instagram.png"
        if skip("social images", social_png.exists()):
            return True
        return run(["python3", SCRIPTS / "generate_social_images.py", "--slug", slug] + force_flag + proj_flag, dry)

    def stage_slide_deck() -> bool:
        # Note: Phase 2 of repurpose_blog.py (step 1/7) already runs this.
        # This step is a safety net — it skips immediately if the HTML exists.
        step("[3/7] Slide deck (Phase-2-redundant; skips if exists)")
        slides_html = REPO / "assets" / "slides" / week / f"{slug}_slides.html"
        if skip("slide deck", slides_html.exists()):
            return True
        return run(["python3", SCRIPTS / "generate_slide_deck.py", "--slug", slug] + force_flag + proj_flag, dry)

    def stage_ig_reel_brief() -> bool:
        # Phase 2 of repurpose_blog.py also runs this. Skips if ig_reel_brief.md exists.
        step("[4/7] IG reel brief (Phase-2-redundant; skips if exists)")
        if skip("ig reel brief", (ddir / "ig_reel_brief.md").exists()):
            return True
        return run(["python3", SCRIPTS / "generate_ig_reel_brief.py", "--slug", slug, "--week", week] + proj_flag, dry)

    def stage_thumbnail() -> bool:
        # Render depends on the brief — the two stay chained inside this stage.
        step("[5/7] Thumbnail brief")
        ok = True
        tb_done = bool(glob.glob(str(REPO / "content" / "derivatives" / "**" / slug / "thumbnail_brief.json"), recursive=True)) \
            or (ddir / "thumbnail_brief.json").exists()
        if not skip("thumbnail brief", tb_done):
            ok = run(["python3", SCRIPTS / "thumbnail_brief.py", "--input", str(blog)], dry) and ok
        if not args.skip_thumbnail:
            thumb_png = REPO / "assets" / "thumbnails" / f"{slug}_thumbnail.png"
            if not skip("thumbnail render", thumb_png.exists()):
                ok = run(["python3", SCRIPTS / "generate_thumbnail.py", "--blog", str(blog), "--export", "--skip-remotion"], dry) and ok
        return ok

    def stage_worksheet() -> bool:
        # generate_worksheet_html.py runs the outline first if its JSON is missing,
        # then designs the HTML and renders the PDF (skips if HTML+PDF already exist).
        step("[6/7] Worksheet — DS/Life only (Claude-designed HTML → PDF; skips if exists)")
        if niche == "poetry":
            print("  [skip] worksheet — poetry niche has no worksheet")
            return True
        ok = True
        ws_pdf = REPO / "output" / "worksheets" / week / f"{slug}_worksheet.pdf"
        if not skip("worksheet", ws_pdf.exists()):
            ok = run(["python3", SCRIPTS / "generate_worksheet_html.py", "-i", str(blog)], dry)
            if ok:  # manifest build consumes the worksheet output
                ok = run(["node", SCRIPTS / "build-worksheets-manifest.mjs"], dry)
        print("  note: push/deploy to make the gated link live stays MANUAL.")
        return ok

    stages = [
        ("social images", stage_social_images),
        ("slide deck", stage_slide_deck),
        ("ig reel brief", stage_ig_reel_brief),
        ("thumbnail", stage_thumbnail),
        ("worksheet", stage_worksheet),
    ]
    # Fail-collect: a failing stage never cancels its siblings — every future
    # runs to completion and we report per-stage status at the end.
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {name: pool.submit(fn) for name, fn in stages}
        for name, fut in futures.items():
            try:
                results[name] = fut.result()
            except Exception as exc:  # noqa: BLE001 - collect, don't cancel siblings
                print(f"  [FAIL] {name}: {exc}", file=sys.stderr)
                results[name] = False

    # ── 7. Stage to scheduler (stays LAST — consumes the derivatives) ──
    step("[7/7] Stage to scheduler (load_posts)")
    if args.no_stage:
        print("  [skip] staging (--no-stage)")
    else:
        results["load_posts"] = run(["python3", SCRIPTS / "load_posts.py", "--week", week], dry)

    # ── Summary ────────────────────────────────────────────────────
    failed = sorted(name for name, ok in results.items() if not ok)
    succeeded = sorted(name for name, ok in results.items() if ok)
    print(f"\n[summary] succeeded: {', '.join(succeeded) or '(none)'}")
    if failed:
        print(f"[summary] FAILED   : {', '.join(failed)}", file=sys.stderr)

    if failed:
        print(f"\n[done] blog pipeline finished WITH FAILURES for {slug}.")
    else:
        print(f"\n[done] blog pipeline complete for {slug}.")
    print("       Videos (long-form + shorts) are separate: run_voiceover_week.py --audio … --niche "
          f"{niche} --week {week} --slug {slug}")

    if not dry:
        if failed:
            notify("Blog pipeline FAILED", f"{slug}: failed — {', '.join(failed)}"[:200])
        else:
            notify("Blog pipeline ✓", f"{slug}: all stages complete ({len(succeeded)} ok)")

    # SEO manual steps for Medium (topic mode already printed these via produce_blog).
    if not args.topic and not dry and blog.exists():
        steps = seo_manual_steps(extract_seo(blog.read_text(encoding="utf-8")))
        if steps:
            print(f"\n{steps}")

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        raise
    except SystemExit as exc:
        # Fatal early exits use sys.exit("<message>") (blog not found /
        # produce_blog failed) — per-stage failures already notified with the
        # succeeded/failed summary in main(); argparse exits stay silent.
        if isinstance(exc.code, str) and exc.code:
            notify("Blog pipeline FAILED", exc.code[:200])
        raise
    except Exception as exc:
        notify("Blog pipeline FAILED", f"{type(exc).__name__}: {exc}"[:200])
        raise
