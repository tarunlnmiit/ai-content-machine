#!/usr/bin/env python3
"""Generate production guide mapping script sections to B-roll clips.

Maps YouTube voiceover script sections to downloaded B-roll clips with duration,
timing, and DaVinci Resolve assembly steps. Auto-generates SRT with poem lines for gaps.

Usage:
    python3 scripts/generate_production_guide.py --script content/scripts/2026-05-16-slug_yt.md --niche life --vo-markers "0:23,0:59,1:58,2:27,3:08,3:39,4:02" --poem data/kb/poem_enough.txt
"""

import argparse
import json
import re
from pathlib import Path

REPO = Path(__file__).parent.parent

def parse_timestamp(ts: str) -> int:
    """Convert MM:SS or M:SS to seconds."""
    parts = ts.split(":")
    return int(parts[0]) * 60 + int(parts[1])

def format_srt_time(seconds: float) -> str:
    """Format seconds as SRT timestamp: HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def load_poem(poem_input: str) -> list:
    """Load poem lines from file or parse inline text."""
    if not poem_input:
        return []
    try:
        p = Path(poem_input)
        if p.exists() and p.is_file():
            text = p.read_text().strip()
        else:
            text = poem_input
    except (OSError, ValueError):
        text = poem_input
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return lines

def load_video_map(script_stem: str) -> dict:
    """Load VIDEO_MAP.json created by fetch_videos.py --script."""
    video_map_path = Path(f"assets/videos/{script_stem}/VIDEO_MAP.json")
    if not video_map_path.exists():
        print(f"Error: {video_map_path} not found. Run fetch_videos.py --script first.")
        return {}
    with open(video_map_path, "r") as f:
        return json.load(f)

def extract_sections(script_text: str) -> list:
    """Parse script into sections by [BROLL:] markers and section headers."""
    sections = []
    section_pattern = r'^\*\*\[?([^\]]+)\]?\*\*|^## ([^\n]+)'
    broll_pattern = r'\[BROLL:\s*([^\]]+)\]'

    lines = script_text.split('\n')
    current_section = None
    section_text = ""
    word_count = 0

    for line in lines:
        # Check for section header
        header_match = re.match(section_pattern, line)
        if header_match:
            if current_section:
                sections.append({
                    "title": current_section,
                    "words": word_count,
                    "estimated_seconds": int(word_count / 2.3)  # ~130 wpm = ~2.3 words/sec
                })
            current_section = header_match.group(1) or header_match.group(2)
            section_text = ""
            word_count = 0
        else:
            section_text += line + "\n"
            word_count += len(line.split())

    if current_section:
        sections.append({
            "title": current_section,
            "words": word_count,
            "estimated_seconds": int(word_count / 2.3)
        })

    return sections

def extract_broll_cues(script_text: str) -> list:
    """Extract all [BROLL:] descriptions in order."""
    pattern = r'\[BROLL:\s*([^\]]+)\]'
    return [m.group(1).strip() for m in re.finditer(pattern, script_text)]

def generate_srt(vo_markers: list, clip_durations: dict, poem_lines: list, script_stem: str, full_poem: bool = False) -> str:
    """Generate SRT with poem lines. If full_poem=True, distribute all lines across full VO duration."""
    if not poem_lines:
        return ""

    srt_entries = []

    if full_poem and vo_markers and len(vo_markers) >= 2:
        total_duration = vo_markers[-1] - vo_markers[0]
        line_duration = total_duration / len(poem_lines)

        for idx, line in enumerate(poem_lines):
            start_ts = vo_markers[0] + (idx * line_duration)
            end_ts = vo_markers[0] + ((idx + 1) * line_duration)
            entry_idx = idx + 1
            srt_entries.append(f"{entry_idx}\n{format_srt_time(start_ts)} --> {format_srt_time(end_ts)}\n{line}\n")
    else:
        if not vo_markers or len(vo_markers) < 2:
            return ""

        poem_idx = 0
        for sec_idx in range(len(vo_markers) - 1):
            start_ts = vo_markers[sec_idx]
            end_ts = vo_markers[sec_idx + 1]
            vo_duration = end_ts - start_ts
            clip_duration = clip_durations.get(sec_idx, 0)
            gap = vo_duration - clip_duration

            if gap <= 0 or poem_idx >= len(poem_lines):
                continue

            fade_start = start_ts + clip_duration
            fade_end = min(fade_start + gap, end_ts)

            entry_idx = len(srt_entries) + 1
            line = poem_lines[poem_idx]
            srt_entries.append(f"{entry_idx}\n{format_srt_time(fade_start)} --> {format_srt_time(fade_end)}\n{line}\n")
            poem_idx += 1

    if not srt_entries:
        return ""

    srt_content = "\n".join(srt_entries)
    srt_path = Path(f"content/scripts/{script_stem}.srt")
    srt_path.parent.mkdir(parents=True, exist_ok=True)
    srt_path.write_text(srt_content, encoding="utf-8")
    return str(srt_path)

def generate_guide(script_path: str, niche: str, vo_markers: list = None, poem_lines: list = None, full_poem: bool = False) -> tuple:
    """Generate production guide matching script sections to clips. Returns (guide_text, srt_path)."""
    with open(script_path, "r") as f:
        script_text = f.read()

    script_stem = Path(script_path).stem
    video_map = load_video_map(script_stem)

    if not video_map:
        return "", ""

    broll_cues = extract_broll_cues(script_text)
    sections = extract_sections(script_text)

    # Build clip-to-cue mapping
    clip_by_cue = {}
    clip_durations = {}
    for filename, meta in video_map.items():
        cue_idx = meta.get("section_cue", 0)
        if cue_idx not in clip_by_cue:
            clip_by_cue[cue_idx] = []
        clip_by_cue[cue_idx].append((filename, meta))
        if cue_idx not in clip_durations or meta.get("duration", 0) > clip_durations[cue_idx]:
            clip_durations[cue_idx] = meta.get("duration", 0)

    # Extract title from script header
    title_match = re.search(r'EPISODE TITLE.*:\s*(.+)', script_text)
    title = title_match.group(1).strip() if title_match else "Production Guide"

    # Calculate totals
    total_words = sum(s["words"] for s in sections)
    total_seconds = sum(s["estimated_seconds"] for s in sections)
    minutes = total_seconds // 60
    seconds = total_seconds % 60

    guide = f"""# Production Guide: {title}

## Voiceover Recording

- **Total words:** ~{total_words:,} | **Est. runtime:** {minutes}:{seconds:02d} min
- Record in one continuous take. Edit pauses later.
- Mark `[PAUSE]` points by clapping once — visible in waveform.
- Save to: `assets/audio/{script_stem}_voiceover.wav`

---

## Section → Clip Map

| # | Section | Duration | Est. Read | Clip | Clip Duration |
|---|---------|----------|-----------|------|---------------|
"""

    for sec_idx, section in enumerate(sections):
        clip_info = ""
        if sec_idx in clip_by_cue:
            clips = clip_by_cue[sec_idx]
            names = ", ".join(c[0] for c in clips)
            first_dur = clips[0][1].get('duration', 0)
            clip_info = f"{names} | {first_dur}s"
        else:
            clip_info = "(no clip mapped)"

        guide += f"| {sec_idx + 1} | {section['title']} | {section['estimated_seconds']}s | {section['words']} words | {clip_info} |\n"

    guide += f"""
---

## Available Clips

| Filename | Duration | B-roll Cue | Source |
|----------|----------|-----------|--------|
"""

    for filename, meta in video_map.items():
        cue_idx = meta.get("section_cue", "?")
        cue_text = broll_cues[cue_idx] if isinstance(cue_idx, int) and cue_idx < len(broll_cues) else "custom"
        guide += f"| {filename} | {meta.get('duration', 0)}s | {cue_text} | {meta.get('source', '?')} |\n"

    # Add VO markers + gaps if provided
    srt_path = ""
    if vo_markers and poem_lines:
        vo_marker_pairs = []
        for i in range(len(vo_markers) - 1):
            vo_marker_pairs.append((vo_markers[i], vo_markers[i + 1]))

        guide += f"""
---

## Voiceover Section Markers

| Section | Start | End | Duration | B-roll | Gap |
|---------|-------|-----|----------|--------|-----|
"""
        for sec_idx, (start, end) in enumerate(vo_marker_pairs):
            duration = end - start
            clip_dur = clip_durations.get(sec_idx, 0)
            gap = duration - clip_dur
            guide += f"| {sec_idx} | {format_srt_time(start)} | {format_srt_time(end)} | {duration}s | {clip_dur}s | {gap}s |\n"

        srt_path = generate_srt(vo_markers, clip_durations, poem_lines, script_stem, full_poem)
        guide += f"""
**Poem overlay SRT:** `{srt_path}`

Import to DaVinci Resolve:
1. Text → Import → {srt_path}
2. Animate each line: fade in 0.3s, hold, fade out 0.3s
3. Position over clips during gap sections
"""

    guide += f"""
---

## DaVinci Resolve Assembly Order

1. **Import clips** in section order (_clip_00, _clip_01, etc.)
   - Media Pool → Import → select all clips from `assets/videos/{script_stem}/`

2. **Create timeline** → drag clips in order to video track

3. **Add voiceover audio track**
   - Audio track → drag `assets/audio/{script_stem}_voiceover.wav`
   - Sync with video clips using timeline markers

4. **Trim clips** to match section durations
   - Use trim handles; reference Section → Clip Map above
   - For sections with VO > B-roll: expect gaps filled by poem overlays

5. **Import captions**
   - Generate captions: `python3 scripts/generate_captions.py --slug {script_stem} --format srt`
   - Text → Import → select `.srt` file
   - Adjust timing if needed

6. **Add poem overlay** (if SRT generated)
   - Text → Import → {srt_path or "poetry_overlay.srt"}
   - Position over gaps; animate fade in/out
   - Font: white, sans serif, center

7. **Export**
   - Project → Export → H.264 MP4, 1080p
   - Filename: `assets/video/edited/{script_stem}.mp4`
   - Audio: -20 dB for music/ambient

---

## Spotify Video Podcast

Upload to Spotify for Podcasters:
- Same `.mp4` file → Spotify video podcast
- Audio-only listeners can follow narrative (no visual references in script)
- Check for [PAUSE] markers — they work as natural beat points
"""

    return guide, srt_path

def main():
    parser = argparse.ArgumentParser(description="Generate production guide from YouTube script + clips")
    parser.add_argument("--script", required=True, help="YouTube script file (from ghostwrite.py --format yt)")
    parser.add_argument("--niche", required=True, choices=["ds", "life", "poetry"])
    parser.add_argument("--vo-markers", help="VO section markers as comma-separated timestamps (MM:SS format), e.g. '0:23,0:59,1:58,2:27'")
    parser.add_argument("--poem", help="Path to poem file or inline poem text for gap overlay")
    parser.add_argument("--full-poem", action="store_true", help="Distribute entire poem evenly across full VO duration")
    args = parser.parse_args()

    script_path = Path(args.script)
    if not script_path.exists():
        print(f"Error: {script_path} not found")
        return

    # Parse VO markers
    vo_markers = None
    if args.vo_markers:
        try:
            vo_markers = [parse_timestamp(ts) for ts in args.vo_markers.split(",")]
        except ValueError:
            print(f"Error: Invalid VO markers format. Use MM:SS,MM:SS,... (e.g., '0:23,0:59')")
            return

    # Load poem
    poem_lines = load_poem(args.poem) if args.poem else []

    guide_text, srt_path = generate_guide(str(script_path), args.niche, vo_markers, poem_lines, args.full_poem)
    if not guide_text:
        return

    script_stem = script_path.stem
    guide_path = Path(f"content/scripts/{script_stem}_PRODUCTION_GUIDE.md")
    guide_path.parent.mkdir(parents=True, exist_ok=True)
    guide_path.write_text(guide_text, encoding="utf-8")

    print(f"✓ Production guide saved: {guide_path}")
    if srt_path:
        print(f"✓ Poem overlay SRT saved: {srt_path}")

if __name__ == "__main__":
    main()
