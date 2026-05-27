#!/usr/bin/env python3
"""Prepare Remotion edit plan for a raw talking-head video.

Pipeline:
  1. Whisper transcribe → Caption[] JSON (word timestamps)
  2. ffmpeg silence detection → trim start/end seconds
  3. fetch_videos.py → stock b-roll for [BROLL:] cues
  4. Map b-roll clips to cue timestamps
  5. Write remotion/public/edit-plans/<slug>.json

Usage:
  python3 scripts/prepare_remotion_edit.py \\
    --raw assets/raw/2026-05-21_life_self_dev_...MOV \\
    --script content/scripts/2026-05-22_..._yt.md \\
    --niche life \\
    --slug life_habits
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent
REMOTION_PUBLIC = REPO / "remotion" / "public"
sys.path.insert(0, str(REPO / "scripts"))

# Use homebrew ffmpeg (has libx264); conda env ffmpeg lacks it
FFMPEG_BIN = "/opt/homebrew/bin/ffmpeg"
FFPROBE_BIN = "/opt/homebrew/bin/ffprobe"

# Load .env
env_file = REPO / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ[k] = v.strip('"\'')


def run(cmd: list, capture=True) -> str:
    r = subprocess.run(cmd, capture_output=capture, text=True)
    if r.returncode != 0 and capture:
        print(f"  warn: {' '.join(cmd[:3])} exit {r.returncode}: {r.stderr[-400:]}")
    return r.stdout + r.stderr if capture else ""


def transcribe_whisper(raw: Path, slug: str) -> list:
    """Run whisper CLI as subprocess to avoid PyTorch/OpenMP in-process crash."""
    import tempfile
    print("[whisper] transcribing via CLI subprocess (this takes a minute)…")
    with tempfile.TemporaryDirectory() as tmpdir:
        whisper_bin = Path(sys.executable).parent / "whisper"
        cmd = [
            str(whisper_bin), str(raw),
            "--model", "base",
            "--output_format", "json",
            "--word_timestamps", "True",
            "--output_dir", tmpdir,
        ]
        env = {**os.environ, "KMP_DUPLICATE_LIB_OK": "TRUE"}
        r = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if r.returncode != 0:
            print(f"  whisper error: {r.stderr[-600:]}")
            return []
        out_json = Path(tmpdir) / (Path(raw).stem + ".json")
        if not out_json.exists():
            print("  whisper: no output JSON found")
            return []
        result = json.loads(out_json.read_text())

    captions = []
    for seg in result.get("segments", []):
        for word in seg.get("words", []):
            captions.append({
                "text": word["word"],
                "startMs": round(word["start"] * 1000),
                "endMs": round(word["end"] * 1000),
                "timestampMs": round(word["start"] * 1000),
                "confidence": word.get("probability", None),
            })
    return captions


def detect_silence(raw: Path) -> tuple[float, float]:
    """Return (trim_start_sec, trim_end_sec) using ffmpeg loudnorm + silencedetect."""
    print("[ffmpeg] measuring loudness…")
    out = run([
        FFMPEG_BIN, "-i", str(raw),
        "-map", "0:a",
        "-af", "loudnorm=print_format=json",
        "-f", "null", "/dev/null",
    ])
    thresh = "-35"
    try:
        data = json.loads(out[out.rfind("{"):out.rfind("}") + 1])
        thresh = str(float(data.get("input_thresh", -35)))
    except Exception:
        pass

    print(f"[ffmpeg] silence detect (threshold {thresh}dB)…")
    out2 = run([
        FFMPEG_BIN, "-i", str(raw),
        "-map", "0:a",
        "-af", f"silencedetect=noise={thresh}dB:d=0.5",
        "-f", "null", "/dev/null",
    ])

    # parse silences
    starts = [float(m) for m in re.findall(r"silence_start:\s*([\d.]+)", out2)]
    ends = [float(m) for m in re.findall(r"silence_end:\s*([\d.]+)", out2)]

    # probe total duration
    dur_out = run([
        FFPROBE_BIN, "-v", "quiet", "-print_format", "json",
        "-show_format", str(raw),
    ])
    try:
        duration = float(json.loads(dur_out)["format"]["duration"])
    except Exception:
        duration = 0

    trim_start = 0.0
    trim_end = duration

    if starts and starts[0] < 0.5 and ends:
        trim_start = ends[0]

    if starts and ends and abs(ends[-1] - duration) < 2.0:
        trim_end = starts[-1]

    print(f"[silence] trim {trim_start:.1f}s → {trim_end:.1f}s (duration {duration:.1f}s)")
    return trim_start, trim_end


CLAP_SETTLE_SEC = 1.5       # silence to skip after clap ends
CLAP_PRE_PAD_SEC = 0.10     # cut a bit before clap to remove attack
CLAP_MAX_DURATION = 0.25    # real claps are 50-250ms; >0.25s is speech
CLAP_PEAK_OFFSET_DB = 1.5   # threshold = peak_db + this (stricter = fewer false positives)
CLAP_THRESH_CEILING_DB = -1.5  # absolute ceiling — speech rarely exceeds -1.5 dBFS
CLAP_MIN_PRE_GAP_SEC = 1.0  # require quiet (below threshold) for ≥1s BEFORE clap (kills speech FPs)
CLAP_MAX_REGIONS = 8        # safety: never cut more than this many regions (sanity check)


def detect_claps(raw: Path) -> list[tuple[float, float]]:
    """Find ALL clap sync markers across the full video.

    Real claps signatures:
      - Very short burst (<350ms)
      - Loudness near absolute peak (within ~1.5 dB)
      - Preceded by quiet (no other near-peak audio for 250ms+)

    Returns list of (cut_start, cut_end) intervals after padding.
    """
    # Peak volume across whole video
    out = run([
        FFMPEG_BIN, "-i", str(raw),
        "-vn", "-af", "volumedetect", "-f", "null", "/dev/null",
    ])
    m = re.search(r"max_volume:\s*([-\d.]+)\s*dB", out)
    if not m:
        print("[clap] volumedetect failed, skipping clap detection")
        return []

    peak_db = float(m.group(1))
    # When audio is clipped (peak ~0), relative threshold collapses → false positives.
    # Use absolute near-clip threshold instead: only sustained near-saturation counts.
    if peak_db > -1.0:
        thresh_db = -0.3
        print(f"[clap] peak={peak_db:.1f}dB (clipped) → near-clip threshold={thresh_db}dB")
    else:
        thresh_db = min(peak_db + CLAP_PEAK_OFFSET_DB, CLAP_THRESH_CEILING_DB)
        print(f"[clap] peak={peak_db:.1f}dB → relative threshold={thresh_db:.1f}dB")

    # silencedetect with HIGH threshold: "silence" here = audio below near-peak level
    # → silence_end = moment audio rises above near-peak (potential clap start)
    # → next silence_start = moment audio drops below near-peak (clap end)
    out2 = run([
        FFMPEG_BIN, "-i", str(raw),
        "-vn", "-af", f"silencedetect=noise={thresh_db:.1f}dB:d={CLAP_MIN_PRE_GAP_SEC}",
        "-f", "null", "/dev/null",
    ])

    silence_starts = sorted(float(x) for x in re.findall(r"silence_start:\s*([\d.]+)", out2))
    silence_ends = sorted(float(x) for x in re.findall(r"silence_end:\s*([\d.]+)", out2))

    # Pair each silence_end (clap start) with the immediately following silence_start (clap end).
    # Requiring d=CLAP_MIN_PRE_GAP_SEC above guarantees ≥250ms of pre-clap quiet by construction.
    claps: list[tuple[float, float]] = []
    for clap_start in silence_ends:
        clap_end = next((s for s in silence_starts if s > clap_start), None)
        if clap_end is None:
            continue
        burst = clap_end - clap_start
        if burst < CLAP_MAX_DURATION:
            claps.append((clap_start, clap_end))

    if not claps:
        print("[clap] no claps detected")
        return []

    # Merge overlapping padded regions
    merged: list[tuple[float, float]] = []
    for cs, ce in claps:
        padded_start = max(0.0, cs - CLAP_PRE_PAD_SEC)
        padded_end = ce + CLAP_SETTLE_SEC
        if merged and padded_start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], padded_end))
        else:
            merged.append((padded_start, padded_end))

    if len(merged) > CLAP_MAX_REGIONS:
        print(f"[clap] WARN: detected {len(merged)} regions > sanity cap {CLAP_MAX_REGIONS} — "
              "likely false positives (clipped audio?). Skipping clap cuts.")
        return []

    print(f"[clap] detected {len(merged)} clap region(s):")
    for cs, ce in merged:
        print(f"  cut {cs:.2f}s → {ce:.2f}s ({ce - cs:.2f}s)")
    return merged


def build_cut_segments(
    trim_start: float,
    trim_end: float,
    clap_cuts: list[tuple[float, float]],
) -> list[dict]:
    """Subtract clap cut regions from [trim_start, trim_end] to get keep-segments."""
    segments: list[dict] = []
    cursor = trim_start
    for cs, ce in clap_cuts:
        if ce <= trim_start or cs >= trim_end:
            continue
        cs_clamped = max(cs, trim_start)
        ce_clamped = min(ce, trim_end)
        if cs_clamped > cursor:
            segments.append({"startSec": round(cursor, 2), "endSec": round(cs_clamped, 2)})
        cursor = max(cursor, ce_clamped)
    if cursor < trim_end:
        segments.append({"startSec": round(cursor, 2), "endSec": round(trim_end, 2)})
    return segments


def parse_broll_cues(script_path: Path) -> list:
    """Extract [BROLL: description] markers from YT script."""
    text = script_path.read_text()
    return re.findall(r"\[BROLL:\s*([^\]]+)\]", text)


def parse_screen_cues(script_path: Path) -> list:
    """Extract [SCREEN: description] markers from YT script (ds niche)."""
    text = script_path.read_text()
    return re.findall(r"\[SCREEN:\s*([^\]]+)\]", text)


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".avif"}


def collect_screen_images(script_path: Path, slug: str) -> list:
    """For ds niche: copy PNGs from assets/script_images/<stem>/ as b-roll cues."""
    stem_dir = REPO / "assets" / "script_images" / script_path.stem
    if not stem_dir.exists():
        print(f"[screen] no script_images dir at {stem_dir}")
        return []

    images = sorted([p for p in stem_dir.iterdir() if p.suffix.lower() in IMAGE_EXTS])
    if not images:
        print(f"[screen] no images found in {stem_dir}")
        return []

    cue_descriptions = parse_screen_cues(script_path)
    broll_dst = REMOTION_PUBLIC / "broll" / slug
    broll_dst.mkdir(parents=True, exist_ok=True)

    print(f"[screen] {len(images)} images available ({len(cue_descriptions)} [SCREEN:] markers)")
    clips: list = []
    for i, src in enumerate(images):
        dst = broll_dst / f"cue-{i}{src.suffix}"
        shutil.copy2(src, dst)
        desc = cue_descriptions[i] if i < len(cue_descriptions) else "screen capture"
        clips.append({
            "id": f"cue-{i}",
            "description": desc,
            "clipFile": f"broll/{slug}/cue-{i}{src.suffix}",
        })
    return clips


BROLL_DURATION_SEC = 5.0
BROLL_JITTER_SEC = 2.0  # ±jitter around evenly-spaced timestamps


def fetch_and_copy_broll(script_path: Path, niche: str, slug: str, cue_descriptions: list) -> list:
    """Invoke fetch_videos.py, copy ALL downloaded clips, return list of BrollCue dicts."""
    print(f"[broll] fetching stock clips (script has {len(cue_descriptions)} [BROLL:] markers)…")
    cmd = [
        "python3", str(REPO / "scripts" / "fetch_videos.py"),
        "--script", str(script_path),
        "--niche", niche,
    ]
    run(cmd, capture=False)

    broll_src = REPO / "assets" / "videos" / script_path.stem
    broll_dst = REMOTION_PUBLIC / "broll" / slug
    broll_dst.mkdir(parents=True, exist_ok=True)

    clips: list = []
    if not broll_src.exists():
        return clips
    map_file = broll_src / "VIDEO_MAP.json"
    if not map_file.exists():
        return clips

    vid_map = json.loads(map_file.read_text())
    downloaded = [
        (fname, meta) for fname, meta in vid_map.items()
        if meta.get("downloaded") and (broll_src / fname).exists()
    ]

    print(f"[broll] {len(downloaded)} clips available, using all")
    for i, (fname, _) in enumerate(downloaded):
        src = broll_src / fname
        dst = broll_dst / f"cue-{i}{src.suffix}"
        shutil.copy2(src, dst)
        desc = cue_descriptions[i] if i < len(cue_descriptions) else "ambient b-roll"
        clips.append({
            "id": f"cue-{i}",
            "description": desc,
            "clipFile": f"broll/{slug}/cue-{i}{src.suffix}",
        })
    return clips


def assign_broll_timestamps(
    clips: list,
    trim_start: float,
    trim_end: float,
) -> list:
    """Evenly distribute b-roll cues across timeline with small jitter."""
    import random
    edited_duration = trim_end - trim_start
    if not clips or edited_duration <= 0:
        return clips

    n = len(clips)
    interval = edited_duration / (n + 1)
    # Avoid first/last 3s
    min_start = trim_start + 3.0
    max_start = trim_end - BROLL_DURATION_SEC - 3.0

    rng = random.Random(42)  # deterministic jitter for reproducible plans
    result = []
    for i, clip in enumerate(clips):
        base = trim_start + interval * (i + 1)
        jitter = rng.uniform(-BROLL_JITTER_SEC, BROLL_JITTER_SEC)
        start_sec = max(min_start, min(max_start, base + jitter))
        result.append({**clip, "startSec": round(start_sec, 2), "durationSec": BROLL_DURATION_SEC})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True)
    parser.add_argument("--script", required=True)
    parser.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    parser.add_argument("--slug", required=True)
    args = parser.parse_args()

    raw = Path(args.raw)
    script = Path(args.script)
    slug = args.slug

    print(f"\n=== Preparing Remotion edit: {slug} ===\n")

    # 1. Transcribe (skip if cached)
    captions_file = f"captions/{slug}.json"
    captions_path = REMOTION_PUBLIC / "captions" / f"{slug}.json"
    captions_path.parent.mkdir(parents=True, exist_ok=True)
    if captions_path.exists() and captions_path.stat().st_size > 100:
        captions = json.loads(captions_path.read_text())
        print(f"[captions] cached: {len(captions)} words ({captions_path.name})")
    else:
        captions = transcribe_whisper(raw, slug)
        captions_path.write_text(json.dumps(captions, indent=2))
        print(f"[captions] {len(captions)} words → {captions_path}")

    # 2. Silence detection + multi-clap detection
    trim_start, trim_end = detect_silence(raw)
    clap_cuts = detect_claps(raw)

    # 3. B-roll — ds uses [SCREEN:] + script_images/; life/poetry use [BROLL:] + stock video
    if args.niche == "ds":
        clips = collect_screen_images(script, slug)
    else:
        cue_descriptions = parse_broll_cues(script)
        print(f"[broll] found {len(cue_descriptions)} [BROLL:] cues in script")
        clips = fetch_and_copy_broll(script, args.niche, slug, cue_descriptions)
    clips = assign_broll_timestamps(clips, trim_start, trim_end)

    # 4. Convert raw to MP4 with loudnorm baked in (Chrome needs MP4 + louder audio)
    mp4_dest = REMOTION_PUBLIC / "videos" / f"{slug}.mp4"
    mp4_dest.parent.mkdir(parents=True, exist_ok=True)
    if not mp4_dest.exists():
        print(f"[ffmpeg] converting {raw.name} → {slug}.mp4 with loudnorm -16 LUFS…")
        r = subprocess.run([
            FFMPEG_BIN, "-i", str(raw),
            "-c:v", "libx264", "-profile:v", "main", "-level", "4.0",
            "-pix_fmt", "yuv420p", "-preset", "fast", "-crf", "22",
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
            str(mp4_dest), "-y",
        ], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  ffmpeg error: {r.stderr[-400:]}")
        else:
            print(f"  → {mp4_dest}")
    else:
        print(f"[ffmpeg] {slug}.mp4 already exists, skipping conversion")

    # Build cut segments: subtract every clap region from [trim_start, trim_end]
    cut_segments = build_cut_segments(trim_start, trim_end, clap_cuts)
    print(f"[cuts] {len(cut_segments)} keep-segment(s) after removing {len(clap_cuts)} clap region(s)")
    total_duration = sum(s["endSec"] - s["startSec"] for s in cut_segments)

    plan = {
        "slug": slug,
        "niche": args.niche,
        "rawVideo": f"videos/{slug}.mp4",
        "durationSec": round(total_duration, 2),
        "silenceTrimStartSec": trim_start,
        "silenceTrimEndSec": trim_end,
        "cutSegments": cut_segments,
        "brollCues": clips,
        "captionsFile": captions_file,
    }

    plan_path = REMOTION_PUBLIC / "edit-plans" / f"{slug}.json"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(json.dumps(plan, indent=2))
    print(f"\n[done] edit plan → {plan_path}")

    print("\n=== Next steps ===")
    print(f"  cd remotion && npx remotion studio")
    print(f"  # Select composition '{slug}' in Studio to preview")
    print(f"  npx remotion render {_composition_id(slug)} --output ../assets/video/edited/{slug}.mp4")


def _composition_id(slug: str) -> str:
    parts = slug.replace("-", "_").split("_")
    return "".join(w.capitalize() for w in parts if w)


if __name__ == "__main__":
    main()
