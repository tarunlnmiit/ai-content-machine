#!/usr/bin/env python3
"""Generate captions for audio/video using OpenAI Whisper (free, open-source)."""

import json
import subprocess
import argparse
import tempfile
from pathlib import Path
from _console import console, spinner

REPO = Path(__file__).parent.parent
AUDIO_DIR = REPO / "assets" / "audio"
VIDEO_DIR = REPO / "assets" / "video" / "edited"


def whisper_json_to_remotion_captions(whisper_json_path: Path) -> list[dict]:
    """Convert Whisper JSON segments to @remotion/captions Caption[] format."""
    data = json.loads(whisper_json_path.read_text())
    captions = []
    for seg in data.get("segments", []):
        captions.append({
            "text": seg["text"].strip(),
            "startMs": round(seg["start"] * 1000),
            "endMs": round(seg["end"] * 1000),
            "timestampMs": round(seg["start"] * 1000),
            "confidence": None,
        })
    return captions


def generate_captions(
    input_path: Path,
    output_format: str = "srt",
    output_path: Path | None = None,
    model: str = "base",
) -> Path:
    """Generate captions using Whisper CLI. Requires: pip install openai-whisper"""
    # For remotion JSON format, run Whisper as JSON then convert
    whisper_format = "json" if output_format == "remotion_json" else output_format

    # Use a temp dir for Whisper output so we control placement
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        cmd = [
            "whisper",
            str(input_path),
            "--language", "English",
            "--model", model,
            "--output_format", whisper_format,
            "--output_dir", str(tmp_dir),
        ]

        with spinner() as progress:
            progress.add_task(f"Transcribing {input_path.name}...")
            try:
                subprocess.run(cmd, check=True, capture_output=True)
            except FileNotFoundError:
                console.print("[error]Error:[/error] whisper not found.")
                console.print("Install: [bold]pip install openai-whisper[/bold]")
                exit(1)
            except subprocess.CalledProcessError as e:
                console.print("[error]Error:[/error] Whisper failed")
                if e.stderr:
                    console.print(e.stderr.decode())
                exit(1)

        whisper_out = tmp_dir / f"{input_path.stem}.{whisper_format}"

        if output_format == "remotion_json":
            captions = whisper_json_to_remotion_captions(whisper_out)
            dest = output_path or (input_path.parent / f"{input_path.stem}.captions.json")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(json.dumps(captions, indent=2))
            caption_file = dest
        else:
            dest = output_path or (input_path.parent / f"{input_path.stem}.{output_format}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            whisper_out.rename(dest)
            caption_file = dest

    console.print(f"[success]✓ Saved:[/success] {caption_file.relative_to(REPO)}")
    return caption_file


parser = argparse.ArgumentParser(
    description="Generate captions from audio/video using OpenAI Whisper (free)."
)
parser.add_argument("--audio", help="Path to audio file (WAV/MP3/MOV). Takes priority over --slug.")
parser.add_argument(
    "--slug",
    help="File slug — looks for assets/audio/{slug}_voiceover.wav, then assets/video/edited/{slug}.mp4",
)
parser.add_argument(
    "--format",
    default="srt",
    choices=["srt", "vtt", "txt", "remotion_json"],
    help="Caption format. Use remotion_json for @remotion/captions Caption[] JSON.",
)
parser.add_argument("--output", help="Output file path. Defaults to same dir as input.")
parser.add_argument(
    "--model",
    default="base",
    choices=["tiny", "base", "small", "medium", "large"],
    help="Whisper model size (larger = more accurate, slower)",
)
args = parser.parse_args()

if args.audio:
    input_path = Path(args.audio)
    if not input_path.is_absolute():
        input_path = REPO / input_path
elif args.slug:
    audio_guess = AUDIO_DIR / f"{args.slug}_voiceover.wav"
    video_guess = VIDEO_DIR / f"{args.slug}.mp4"
    if audio_guess.exists():
        input_path = audio_guess
    elif video_guess.exists():
        input_path = video_guess
    else:
        console.print(f"[error]Error:[/error] No file found for slug '[bold]{args.slug}[/bold]'")
        console.print(f"  Tried: {audio_guess.relative_to(REPO)}")
        console.print(f"  Tried: {video_guess.relative_to(REPO)}")
        available = sorted(list(AUDIO_DIR.glob("*.wav")) + list(AUDIO_DIR.glob("*.mp3")))
        if available:
            console.print("\n[info]Available audio files:[/info]")
            for f in available:
                console.print(f"  {f.name}")
        exit(1)
else:
    parser.error("Provide [bold]--audio <path>[/bold] or [bold]--slug <slug>[/bold]")

if not input_path.exists():
    console.print(f"[error]Error:[/error] File not found: {input_path}")
    exit(1)

console.print(f"[info]Input:[/info]  {input_path.relative_to(REPO)}")
console.print(f"[info]Format:[/info] {args.format.upper()}")
console.print(f"[info]Model:[/info]  {args.model}")
console.print()

output_path = Path(args.output) if args.output else None
if output_path and not output_path.is_absolute():
    output_path = REPO / output_path

generate_captions(input_path, args.format, output_path, args.model)
