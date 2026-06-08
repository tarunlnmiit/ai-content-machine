#!/usr/bin/env python3
"""Auto-generate YouTube Shorts metadata from clip content.

Transcribes each short clip via Whisper, then asks Claude to write
the optimal title, description, and tags for that specific clip.

Usage:
  python3 scripts/generate_shorts_meta.py --slug <slug>
  python3 scripts/generate_shorts_meta.py --slug <slug> --indices 1,2,3
  python3 scripts/generate_shorts_meta.py --slug <slug> --force
  python3 scripts/generate_shorts_meta.py --slug <slug> --whisper-model small
  python3 scripts/generate_shorts_meta.py --slug <clips-slug> --meta-slug <derivative-slug>
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).parent.parent
sys.path.insert(0, str(REPO / "scripts"))

from lib.video_utils import parse_srt  # noqa: E402
from lib.claude_cli import call_claude  # noqa: E402

NICHE_CONTEXTS = {
    "ds": {
        "label": "Data Science / Python tutorial",
        "audience": "learners and aspiring data scientists",
        "title_tip": "Name the specific skill, mistake, or concept. Be precise, not vague.",
        "temperature": 0.4,
    },
    "life": {
        "label": "Life & self-development",
        "audience": "people building habits and working toward goals",
        "title_tip": "Personal and direct. First-person or second-person. Relatable, not preachy.",
        "temperature": 0.85,
    },
    "poetry": {
        "label": "Poetry and quotes",
        "audience": "introspective readers who appreciate language",
        "title_tip": "Lead with emotion or image. Lyrical hook. Let the words do the work.",
        "temperature": 1.15,
    },
}

STUB_RE = re.compile(r"^short_\d+ (title|description) — fill in")


def detect_niche(slug: str) -> str:
    s = slug.lower()
    if "data_science" in s or "data-science" in s or "python" in s or "_tech" in s:
        return "ds"
    if "poetry" in s or "quotes" in s:
        return "poetry"
    return "life"


def srt_to_text(srt_path: Path) -> str:
    cues = parse_srt(srt_path)
    return " ".join(c["text"] for c in cues).strip()


def whisper_transcribe(clip: Path, model: str) -> str:
    whisper_bin = Path(sys.executable).parent / "whisper"
    env = {**os.environ, "KMP_DUPLICATE_LIB_OK": "TRUE"}
    with tempfile.TemporaryDirectory() as tmpdir:
        cmd = [
            str(whisper_bin), str(clip),
            "--model", model,
            "--output_format", "srt",
            "--output_dir", tmpdir,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if r.returncode != 0:
            print(f"  [whisper] failed: {r.stderr[-300:]}", file=sys.stderr)
            return ""
        srt_tmp = Path(tmpdir) / (clip.stem + ".srt")
        if not srt_tmp.exists():
            return ""
        return srt_to_text(srt_tmp)


def get_transcript(idx: int, slug: str, clip: Path, whisper_model: str) -> str:
    # 1. Segment SRT left by clip_shorts.py
    seg_srt = REPO / "assets" / "video" / "_work" / slug / "shorts" / f"seg_{idx:02d}.srt"
    if seg_srt.exists():
        text = srt_to_text(seg_srt)
        if text:
            print(f"  [srt] using existing seg_{idx:02d}.srt")
            return text

    # 2. Whisper on the short clip itself
    print(f"  [whisper] transcribing short_{idx:02d} (model={whisper_model})…")
    return whisper_transcribe(clip, whisper_model)


def claude_metadata(transcript: str, hook_line: str, niche: str) -> dict | None:
    ctx = NICHE_CONTEXTS[niche]
    hook_section = f"\nOpening hook line: {hook_line}" if hook_line else ""
    prompt = f"""You write YouTube Shorts metadata for a content creator.

Niche: {ctx['label']}
Audience: {ctx['audience']}
Creator voice: Analytical but warm, personal examples, no jargon without context.
Banned words: "In conclusion", "Dive into", "Leverage", "Game-changer", "Synergy"

Clip transcript:
{transcript[:3000]}
{hook_section}

Write YouTube Shorts metadata for this clip.

Rules:
- title: Under 60 chars. Hook in first 3 words. {ctx['title_tip']} No trailing ellipsis.
- description: 2-3 punchy sentences in creator voice. End with 2-3 relevant hashtags including #Shorts.
- tags: 5-8 strings, mix broad + specific. No "#" prefix in tags array.

Return ONLY valid JSON, no prose, no markdown fences:
{{"title": "...", "description": "...", "tags": [...]}}"""

    try:
        out = call_claude(prompt, cache=True, temperature=ctx["temperature"], timeout=90,
                          progress_label=f"generating metadata").strip()
    except RuntimeError as e:
        print(f"  [claude] error: {e}", file=sys.stderr)
        return None

    m = re.search(r"\{.*\}", out, re.DOTALL)
    if not m:
        print(f"  [claude] no JSON in output:\n{out[:300]}", file=sys.stderr)
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError as e:
        print(f"  [claude] JSON parse error: {e}", file=sys.stderr)
        return None


def is_stub(entry: dict) -> bool:
    title = entry.get("title", "")
    desc = entry.get("description", "")
    return bool(STUB_RE.match(title) or STUB_RE.match(desc))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug", required=True, help="Content slug (matches derivative dir name)")
    ap.add_argument("--whisper-model", default="base",
                    choices=["tiny", "base", "small", "medium", "large"])
    ap.add_argument("--force", action="store_true",
                    help="Overwrite all entries, not just stubs")
    ap.add_argument("--indices", default="",
                    help="Comma-separated indices to regenerate (e.g. 1,2,5). Default: all stubs.")
    ap.add_argument("--meta-slug", default="",
                    help="Derivative dir slug when it differs from the clips slug.")
    args = ap.parse_args()

    slug = args.slug
    meta_slug = args.meta_slug or slug
    shorts_dir = REPO / "assets" / "video" / "edited" / "shorts"
    meta_path = REPO / "content" / "derivatives" / meta_slug / "youtube_shorts_metadata.json"

    # Discover clips
    clips_raw = list(shorts_dir.glob(f"{slug}_short_*.mp4"))
    if not clips_raw:
        sys.exit(f"No clips found: {shorts_dir}/{slug}_short_*.mp4\nRun clip_shorts.py first.")

    def clip_idx(p: Path) -> int:
        m = re.search(r"short_(\d+)", p.stem)
        return int(m.group(1)) if m else 999

    clips = sorted(clips_raw, key=clip_idx)
    print(f"=== generate_shorts_meta: {slug} ===")
    print(f"  {len(clips)} clips found")

    # Load manifest (optional hook_line per clip)
    manifest_path = shorts_dir / f"{slug}_shorts_manifest.json"
    if not manifest_path.exists():
        manifest_path = shorts_dir / f"{meta_slug}_shorts_manifest.json"
    manifest: list = []
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
            print(f"  manifest loaded ({len(manifest)} entries)")
        except (json.JSONDecodeError, OSError):
            pass

    # Load existing metadata
    existing_meta: dict = {"long_form_url": "", "shorts": []}
    if meta_path.exists():
        try:
            raw = json.loads(meta_path.read_text())
            if isinstance(raw, dict) and "shorts" in raw:
                existing_meta = raw
            elif isinstance(raw, list):
                existing_meta = {"long_form_url": "", "shorts": raw}
        except (json.JSONDecodeError, OSError):
            pass

    long_form_url = existing_meta.get("long_form_url", "")
    existing_shorts: list = existing_meta.get("shorts", [])

    # Determine which indices to regenerate
    if args.indices:
        target_indices = {int(i.strip()) for i in args.indices.split(",") if i.strip()}
    else:
        target_indices = None  # meaning: all stubs (or all if --force)

    niche = detect_niche(slug)
    print(f"  niche: {niche}  (auto-detected)")

    # Build output list (start from existing, fill 14 slots)
    output_shorts: list = list(existing_shorts)
    while len(output_shorts) < 14:
        output_shorts.append({})

    for clip in clips:
        idx = clip_idx(clip)
        if idx >= 14:
            print(f"  skip {clip.name} (index {idx} >= 14)")
            continue

        # Decide whether to regenerate this index
        current = output_shorts[idx] if idx < len(output_shorts) else {}
        if target_indices is not None:
            if idx not in target_indices:
                continue
        elif not args.force:
            if current and not is_stub(current):
                print(f"  [{idx:02d}] skip — real metadata exists (use --force to overwrite)")
                continue

        print(f"\n  [{idx:02d}] {clip.name}")

        # Transcribe
        transcript = get_transcript(idx, slug, clip, args.whisper_model)
        if not transcript:
            print(f"  [{idx:02d}] WARN: empty transcript — skipping")
            continue

        # Hook line from manifest if available
        hook_line = ""
        if idx < len(manifest):
            hook_line = manifest[idx].get("hook_line", "")

        # Generate metadata via Claude
        meta = claude_metadata(transcript, hook_line, niche)
        if not meta:
            print(f"  [{idx:02d}] WARN: Claude returned nothing — skipping")
            continue

        entry = {
            "title": meta.get("title", ""),
            "description": meta.get("description", ""),
            "tags": meta.get("tags", []),
            "hook_visual": current.get("hook_visual", ""),
            "end_screen_cta": current.get("end_screen_cta", ""),
        }
        output_shorts[idx] = entry
        print(f"  [{idx:02d}] title: {entry['title']}")

    # Write
    result = {"long_form_url": long_form_url, "shorts": output_shorts}
    meta_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\n✓ wrote → {meta_path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
