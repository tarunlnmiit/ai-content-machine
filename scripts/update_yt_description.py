#!/Users/tarungupta/miniconda3/envs/content_engine_env/bin/python3.14
"""
update_yt_description.py — Update the description of an already-published YouTube video.

USAGE:
    python3 scripts/update_yt_description.py \\
        --video-url "https://youtu.be/XXXXXXXXXXX" \\
        --channel "Breath of Data Science" \\
        --github-url "https://github.com/tarunlnmiit/machine_learning/blob/main/python-for-data-science/tutorial-01/first_script.py"

OPTIONS:
    --video-url     Full YouTube URL or short youtu.be URL
    --channel       Channel name (substring) matching a registered channel
    --github-url    GitHub permalink to inject into the description
    --title         Optional label for the GitHub link (default: "Tutorial code")
    --dry-run       Print the updated description without making API changes

NOTES:
    - Idempotent: won't inject the same link twice (guards via <!-- github-code --> marker)
    - Requires the channel to be registered: python3 scripts/upload_youtube.py --register
    - Requires youtube.force-ssl scope (included in ALL_SCOPES in upload_youtube.py)
"""

import argparse
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

sys.path.insert(0, str(Path(__file__).parent))
from lib.github_links import github_yt_description_snippet, has_github_snippet

# Import auth helpers from upload_youtube without re-running its main()
sys.path.insert(0, str(Path(__file__).parent))
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location("upload_youtube", Path(__file__).parent / "upload_youtube.py")
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
get_credentials = _mod.get_credentials
resolve_channel = _mod.resolve_channel


def extract_video_id(url: str) -> str:
    """Extract 11-char video ID from any YouTube URL format."""
    patterns = [
        r"youtu\.be/([A-Za-z0-9_-]{11})",
        r"[?&]v=([A-Za-z0-9_-]{11})",
        r"youtube\.com/embed/([A-Za-z0-9_-]{11})",
    ]
    for pattern in patterns:
        m = re.search(pattern, url)
        if m:
            return m.group(1)
    # Try bare ID
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url.strip()):
        return url.strip()
    raise ValueError(f"Could not extract video ID from: {url}")


def fetch_video_snippet(youtube, video_id: str) -> dict:
    """Fetch current snippet for a video. Raises if not found."""
    resp = youtube.videos().list(part="snippet", id=video_id).execute()
    items = resp.get("items", [])
    if not items:
        raise ValueError(f"Video not found or not accessible: {video_id}")
    return items[0]["snippet"]


def update_description(youtube, video_id: str, snippet: dict, new_description: str) -> None:
    """Update the video description. Strips read-only fields before sending."""
    writable = {
        "title": snippet["title"],
        "description": new_description,
        "categoryId": snippet.get("categoryId", "28"),
        "tags": snippet.get("tags", []),
        "defaultLanguage": snippet.get("defaultLanguage", "en"),
        "defaultAudioLanguage": snippet.get("defaultAudioLanguage", "en"),
    }
    youtube.videos().update(
        part="snippet",
        body={"id": video_id, "snippet": writable},
    ).execute()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update description of a published YouTube video.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--video-url", required=True, help="YouTube URL or video ID")
    parser.add_argument("--channel", default=None, help="Channel name (substring) or ID")
    parser.add_argument("--github-url", required=True, help="GitHub permalink to inject")
    parser.add_argument("--title", default=None, help="Label for GitHub link in description")
    parser.add_argument("--dry-run", action="store_true", help="Print updated description without writing")
    args = parser.parse_args()

    try:
        video_id = extract_video_id(args.video_url)
    except ValueError as e:
        sys.exit(f"ERROR: {e}")

    channel = resolve_channel(args.channel)
    creds = get_credentials(channel["id"])
    youtube = build("youtube", "v3", credentials=creds)

    try:
        snippet = fetch_video_snippet(youtube, video_id)
    except (HttpError, ValueError) as e:
        sys.exit(f"ERROR fetching video: {e}")

    current_desc: str = snippet.get("description", "")

    if has_github_snippet(current_desc):
        print(f"[info] GitHub link already present in description — nothing to do.")
        print(f"Video: https://youtu.be/{video_id}")
        return

    snippet_text = github_yt_description_snippet(args.github_url, args.title)
    new_desc = current_desc.rstrip("\n") + "\n\n" + snippet_text

    if args.dry_run:
        print("=== DRY RUN — updated description ===")
        print(new_desc)
        print("=====================================")
        return

    try:
        update_description(youtube, video_id, snippet, new_desc)
    except HttpError as e:
        sys.exit(f"ERROR updating video: {e}")

    print(f"Updated: https://youtu.be/{video_id}")
    print(f"Channel: {channel['name']}")
    print(f"GitHub link injected: {args.github_url}")
    print(f"\nVerify: https://studio.youtube.com/video/{video_id}/edit")


if __name__ == "__main__":
    main()
