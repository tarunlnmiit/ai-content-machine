#!/usr/bin/env python3
"""AI video B-roll generator.

Reads [BROLL: description] cues from YT script → generates videos.

Backends:
  all     — all active browser backends in parallel, each with a different prompt variant (default)
  hf      — HuggingFace Space: Lightricks/LTX-2-3 (free, no auth)
  ltxio   — ltx.io web app (needs saved session)
  qwen    — qwen.ai Wan 2.1 (needs saved session)
  hunyuan — hunyuanvideo.org (needs saved session)
  muapi   — muapi.ai cloud API (paid)

For "all" mode: each active browser backend fires concurrently with a unique
prompt variant per cue. Output: one .mp4 per backend per cue.

Session setup (one-time):
  python3 scripts/lib/browser_video_client.py --save-session ltxio
  python3 scripts/lib/browser_video_client.py --save-session qwen
  python3 scripts/lib/browser_video_client.py --save-session hunyuan

muapi Models (cheapest → best quality):
  seedance-lite-t2v     — fast, 3-12s, 480p-1080p (default)
  seedance-pro-t2v      — higher quality
  kling-v2.1-master-t2v — premium quality, 5-10s only

Usage:
  python3 scripts/generate_video_ai.py --script content/scripts/my_script.md --niche ds
  python3 scripts/generate_video_ai.py --script content/scripts/my_script.md --niche ds --backend hf
  python3 scripts/generate_video_ai.py --script content/scripts/my_script.md --niche ds --backend muapi --model kling-v2.1-master-t2v
  python3 scripts/generate_video_ai.py --script content/scripts/my_script.md --niche life --dry-run
"""

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

# Load .env
env_file = REPO / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k, v.strip('"\''))

from lib.claude_cli import call_claude  # noqa: E402

NICHE_STYLE = {
    "ds":      "cinematic tech visualization, clean code aesthetics, data flowing, blue tones, professional",
    "life":    "warm cinematic lifestyle, golden hour, natural light, people in motion, inspirational",
    "poetry":  "dreamlike atmospheric, slow motion, nature textures, bokeh, emotional, artistic",
}

NICHE_ASPECT = {"ds": "16:9", "life": "16:9", "poetry": "16:9"}


NICHE_DURATION = {"ds": 3, "life": 5, "poetry": 8}

BROWSER_MODEL = {
    "hf":      "ltx-2-3",
    "qwen":    "wan-2.1",
    "hunyuan": "wan-2.2-fast",
}


def extract_broll_cues(script_path: Path) -> list[dict]:
    text = script_path.read_text()
    return [
        {"idx": i, "cue": m.group(1).strip()}
        for i, m in enumerate(re.finditer(r'\[BROLL:\s*([^\]]+)\]', text))
    ]


def expand_cue_to_prompt_variants(cue: str, niche: str, count: int) -> list[str]:
    """Use Claude to generate `count` distinct video prompts from one cue."""
    style = NICHE_STYLE.get(niche, "cinematic, high quality")
    prompt = f"""Generate {count} distinct AI video generation prompts for this B-roll cue.

Style: {style}
B-roll cue: {cue}

Rules per prompt:
- 2-3 sentences describing motion, lighting, mood, camera movement
- No text overlays, no visible faces
- Cinematic YouTube B-roll quality
- Each prompt must be meaningfully different (angle, mood, or subject variation)

Return exactly {count} prompts, one per line, no numbering, no quotes."""

    try:
        raw = call_claude(prompt, cache=True, timeout=30).strip()
        variants = [line.strip() for line in raw.splitlines() if line.strip()]
        # Pad or trim to exact count
        while len(variants) < count:
            variants.append(f"{cue}, {style}, cinematic shot, high quality")
        return variants[:count]
    except Exception:
        base = f"{cue}, {style}, cinematic shot"
        return [base] * count


def generate_single_backend(
    cues: list[dict],
    niche: str,
    output_dir: Path,
    slug: str,
    backend: str,
    model: str,
    dry_run: bool,
) -> dict:
    """Single-backend generation (muapi). Returns video_map."""
    aspect = NICHE_ASPECT.get(niche, "16:9")
    duration = NICHE_DURATION.get(niche, 5)
    video_map = {}

    for item in cues:
        idx = item["idx"]
        cue = item["cue"]
        filename = f"{slug}_broll_{idx:02d}_{backend}.mp4"
        filepath = output_dir / filename

        print(f"\n  [{idx}] {cue}")
        variants = expand_cue_to_prompt_variants(cue, niche, 1)
        video_prompt = variants[0]
        print(f"       Prompt: {video_prompt[:80]}...")

        entry = {
            "source": backend,
            "model": model,
            "cue": cue,
            "prompt": video_prompt,
            "aspect_ratio": aspect,
            "duration": duration,
            "downloaded": False,
        }
        video_map[filename] = entry

        if dry_run:
            print(f"       [dry-run] {backend} → {filename}")
            continue

        try:
            from lib.muapi_client import generate_video as muapi_generate, download_video
            print(f"       Generating via {model}...")
            video_url = muapi_generate(prompt=video_prompt, model=model,
                                       aspect_ratio=aspect, duration=duration)
            entry["video_url"] = video_url
            download_video(video_url, filepath)
            entry["downloaded"] = True
            print(f"       ✓ → {filename}")
        except Exception as e:
            print(f"       ✗ {e}")
            entry["error"] = str(e)

    return video_map


async def generate_all_browsers_async(
    cues: list[dict],
    niche: str,
    output_dir: Path,
    slug: str,
    backends: list[str],
    dry_run: bool,
) -> dict:
    """
    Worker pool: each backend is a worker, pulls next cue when free.
    One video per cue. 5 cues + 3 backends = 5 clips, not 15.
    """
    from lib.browser_video_client import generate_worker_pool

    duration = NICHE_DURATION.get(niche, 5)
    video_map = {}
    cue_tasks = []

    print(f"  {len(cues)} cues | {len(backends)} workers ({', '.join(backends)})")

    for item in cues:
        idx = item["idx"]
        cue = item["cue"]
        print(f"\n  [{idx}] {cue}")
        variants = expand_cue_to_prompt_variants(cue, niche, 1)
        prompt = variants[0]
        print(f"       Prompt: {prompt[:80]}...")

        # Filename uses placeholder — backend assigned at runtime by pool
        # Use idx as key; rename after we know which backend handled it
        cue_tasks.append({
            "prompt": prompt,
            "output_path": output_dir / f"{slug}_broll_{idx:02d}_BACKEND.mp4",
            "duration_sec": duration,
            "_idx": idx,
            "_cue": cue,
            "_slug": slug,
            "_output_dir": output_dir,
        })

    if dry_run:
        print(f"\n  [dry-run] {len(cues)} cues → {len(backends)} workers, one clip per cue")
        for t in cue_tasks:
            print(f"    cue {t['_idx']}: {t['prompt'][:70]}...")
        return video_map

    print(f"\n  Starting worker pool...")
    results = await generate_worker_pool(cue_tasks, backends)

    for r in results:
        idx = r["_idx"]
        backend = r["backend"]
        # Rename placeholder path to actual backend name
        final_path = output_dir / f"{slug}_broll_{idx:02d}_{backend}.mp4"
        placeholder = r["output_path"]
        if r["success"] and placeholder.exists() and placeholder != final_path:
            placeholder.rename(final_path)

        filename = final_path.name
        video_map[filename] = {
            "source": backend,
            "model": BROWSER_MODEL.get(backend, backend),
            "cue": r["_cue"],
            "prompt": r["prompt"],
            "duration": r["duration_sec"],
            "downloaded": r["success"],
            **({"error": r["error"]} if not r["success"] else {}),
        }

    return video_map


def main():
    parser = argparse.ArgumentParser(description="Generate AI video B-roll from YT script BROLL cues")
    parser.add_argument("--script", required=True, help="YT script .md with [BROLL:] cues")
    parser.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    parser.add_argument(
        "--backend", default="all",
        choices=["all", "hf", "qwen", "hunyuan", "muapi"],
        help=(
            "all=all active browser backends parallel (default); "
            "hf/qwen/hunyuan=single browser backend; "
            "muapi=paid API"
        ),
    )
    parser.add_argument("--model", default="seedance-lite-t2v",
                        choices=["seedance-lite-t2v", "seedance-pro-t2v", "kling-v2.1-master-t2v"],
                        help="muapi model (only used with --backend muapi)")
    parser.add_argument("--dry-run", action="store_true", help="Show prompts, skip generation")
    args = parser.parse_args()

    script_path = Path(args.script)
    if not script_path.exists():
        print(f"Error: {args.script} not found")
        sys.exit(1)

    slug = script_path.stem
    output_dir = REPO / "assets" / "videos" / slug
    output_dir.mkdir(parents=True, exist_ok=True)

    cues = extract_broll_cues(script_path)
    if not cues:
        print("No [BROLL:] cues found in script.")
        sys.exit(0)

    print(f"Script: {slug} | Niche: {args.niche} | Cues: {len(cues)}")

    if args.backend == "muapi":
        print(f"Backend: {args.backend}")
        video_map = generate_single_backend(
            cues=cues, niche=args.niche, output_dir=output_dir,
            slug=slug, backend=args.backend, model=args.model, dry_run=args.dry_run,
        )
    else:
        from lib.browser_video_client import active_backends
        if args.backend == "all":
            backends = active_backends()
        else:
            backends = [args.backend]

        if not backends:
            print("No active backends. Run --save-session or use --backend hf")
            sys.exit(1)

        print(f"Browser backends: {backends} ({'parallel' if len(backends) > 1 else 'single'})")
        video_map = asyncio.run(generate_all_browsers_async(
            cues=cues, niche=args.niche, output_dir=output_dir,
            slug=slug, backends=backends, dry_run=args.dry_run,
        ))

    map_file = output_dir / "VIDEO_MAP.json"
    with open(map_file, "w") as f:
        json.dump(video_map, f, indent=2)

    total = len(video_map)
    downloaded = sum(1 for v in video_map.values() if v["downloaded"])
    failed = total - downloaded
    print(f"\nVideo map → {map_file}")
    print(f"Total: {total} | Downloaded: {downloaded} | Failed: {failed}")
    print(f"Output dir: {output_dir}")

    # Remind about skipped backends
    if args.backend in ("all", "browser", "qwen"):
        from lib.browser_video_client import skipped_backends
        skipped = skipped_backends()
        if skipped:
            print(f"\n⚠️  REMINDER: {', '.join(sorted(skipped))} skipped (SKIP_BACKENDS env).")
            if "qwen" in skipped:
                print("    → Test qwen: python3 scripts/lib/browser_video_client.py --test 'test' --backend qwen")
                print("    → Re-enable: unset SKIP_BACKENDS (or remove from .env)")


if __name__ == "__main__":
    main()
