#!/Users/tarungupta/miniconda3/envs/content_engine_env/bin/python3.14
"""
upload_youtube.py — Upload a video to YouTube with optional scheduled publishing.

FIRST TIME SETUP (run once per channel):
    python3 scripts/upload_youtube.py --register
    → Opens a browser. Sign in with the Google account that owns the channel.
    → Repeat for each additional channel/account.

NORMAL USAGE:
    python3 scripts/upload_youtube.py \\
        --channel "Breath of Life" \\
        --video assets/video/edited/video.mp4 \\
        --title "Your Video Title" \\
        --description "Video description" \\
        --tags "tag1,tag2,tag3" \\
        [--category 22] \\
        [--privacy public|private|unlisted] \\
        [--publish-at "2026-03-28T18:00:00+05:30"]

OPTIONS:
    --register          Authenticate and register a new channel
    --list              List all registered channels
    --channel NAME|ID   Channel name (substring) or channel ID

NOTES:
    - --publish-at schedules the video. The video will be set to 'private'
      and YouTube will automatically publish it at the given time.
    - Without --publish-at, the video is published immediately with --privacy.
    - Category IDs: 10=Music, 20=Gaming, 22=People & Blogs, 24=Entertainment,
                    25=News & Politics, 26=How-to & Style, 28=Science & Technology
    - Tokens are stored at ~/.youtube-mcp/token_<channel_id>.json
    - Registering a channel here also works for fetch_youtube_analytics.py (shared tokens).
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from lib.schedule_calc import get_iso_week

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
TOKEN_DIR = Path.home() / ".youtube-mcp"
CLIENT_SECRET = TOKEN_DIR / "client_secret.json"
REGISTRY_FILE = TOKEN_DIR / "channels.json"

# Full scope set — same as fetch script so one registered token works for both
ALL_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",  # required for commentThreads.insert
]

RESUMABLE_CHUNK_SIZE = 256 * 1024 * 8  # 2 MB chunks


# ── Registry ─────────────────────────────────────────────────────────────────
def load_registry() -> dict:
    """Load channel registry. Format: {channel_id: {name, handle}}"""
    if REGISTRY_FILE.exists():
        return json.loads(REGISTRY_FILE.read_text())
    return {}


def save_registry(registry: dict) -> None:
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    REGISTRY_FILE.write_text(json.dumps(registry, indent=2))


def token_path_for(channel_id: str) -> Path:
    return TOKEN_DIR / f"token_{channel_id}.json"


# ── Auth ─────────────────────────────────────────────────────────────────────
def get_credentials(channel_id: str) -> Credentials:
    """Load and refresh token for a registered channel."""
    token_file = token_path_for(channel_id)

    if not token_file.exists():
        sys.exit(
            f"ERROR: No token found for channel {channel_id}.\n"
            "Run with --register to authenticate this channel."
        )

    creds = Credentials.from_authorized_user_file(str(token_file), ALL_SCOPES)

    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_file.write_text(creds.to_json())
        else:
            sys.exit(
                f"ERROR: Token for channel {channel_id} is expired and cannot be refreshed.\n"
                "Run with --register to re-authenticate this channel."
            )

    return creds


# ── Registration ──────────────────────────────────────────────────────────────
def register_channel() -> None:
    """
    Run a fresh OAuth browser flow and register the channel in the registry.
    Can be run multiple times for different Google accounts / brand accounts.
    """
    if not CLIENT_SECRET.exists():
        sys.exit(
            f"ERROR: client_secret.json not found at {CLIENT_SECRET}\n"
            "Download it from Google Cloud Console → APIs & Services → Credentials."
        )

    print("Opening browser for Google sign-in...")
    print("Sign in with the Google account that owns the channel you want to register.\n")

    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), ALL_SCOPES)
    creds = flow.run_local_server(port=0)

    youtube = build("youtube", "v3", credentials=creds)
    resp = youtube.channels().list(part="id,snippet", mine=True, maxResults=50).execute()
    channels = [
        {
            "id": item["id"],
            "name": item["snippet"]["title"],
            "handle": item["snippet"].get("customUrl", ""),
        }
        for item in resp.get("items", [])
    ]

    if not channels:
        sys.exit("ERROR: No YouTube channels found on this Google account.")

    if len(channels) == 1:
        channel = channels[0]
    else:
        print(f"This Google account has {len(channels)} channels:")
        for i, ch in enumerate(channels, 1):
            handle = f"  {ch['handle']}" if ch["handle"] else ""
            print(f"  [{i}] {ch['name']}{handle}  ({ch['id']})")
        while True:
            raw = input(f"\nWhich channel to register? [1-{len(channels)}]: ").strip()
            if raw.isdigit() and 1 <= int(raw) <= len(channels):
                channel = channels[int(raw) - 1]
                break
            print(f"Please enter a number between 1 and {len(channels)}.")

    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    token_path_for(channel["id"]).write_text(creds.to_json())

    registry = load_registry()
    already_registered = channel["id"] in registry
    registry[channel["id"]] = {"name": channel["name"], "handle": channel["handle"]}
    save_registry(registry)

    action = "Updated" if already_registered else "Registered"
    print(f"\n{action}: {channel['name']}  ({channel['id']})")
    print(f"Token: {token_path_for(channel['id'])}")
    print("\nRegistered channels:")
    for cid, info in load_registry().items():
        handle = f"  {info.get('handle', '')}" if info.get("handle") else ""
        print(f"  • {info['name']}{handle}  ({cid})")


# ── Channel resolution ────────────────────────────────────────────────────────
def resolve_channel(channel_hint: str | None) -> dict:
    """Return {id, name, handle} from the registry. No API call."""
    registry = load_registry()

    if not registry:
        sys.exit(
            "No channels registered yet.\n"
            "Run:  python3 scripts/upload_youtube.py --register"
        )

    channels = [{"id": cid, **info} for cid, info in registry.items()]

    if channel_hint:
        hint_lower = channel_hint.lower()
        matches = [
            ch for ch in channels
            if hint_lower == ch["id"].lower()
            or hint_lower in ch["name"].lower()
            or hint_lower in ch.get("handle", "").lower()
        ]
        if len(matches) == 1:
            ch = matches[0]
            print(f"Channel: {ch['name']} ({ch['id']})")
            return ch
        if len(matches) > 1:
            print(f"Ambiguous --channel '{channel_hint}' matched {len(matches)} channels:")
            for m in matches:
                print(f"  {m['name']} ({m['id']})")
            sys.exit("Use the full channel ID to be specific.")
        sys.exit(
            f"ERROR: No registered channel matching '{channel_hint}'.\n"
            f"Registered: {[ch['name'] for ch in channels]}\n"
            "Run --register to add a new channel."
        )

    if len(channels) == 1:
        ch = channels[0]
        print(f"Channel: {ch['name']} ({ch['id']})")
        return ch

    print("\nRegistered YouTube channels:")
    for i, ch in enumerate(channels, 1):
        handle = f"  {ch.get('handle', '')}" if ch.get("handle") else ""
        print(f"  [{i}] {ch['name']}{handle}  ({ch['id']})")

    while True:
        raw = input(f"\nSelect channel to upload to [1-{len(channels)}]: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(channels):
            ch = channels[int(raw) - 1]
            print(f"Selected: {ch['name']} ({ch['id']})")
            print(f"Tip: use --channel \"{ch['name']}\" to skip this prompt next time.")
            return ch
        print(f"Please enter a number between 1 and {len(channels)}.")


# ── Upload ────────────────────────────────────────────────────────────────────
def upload_video(
    youtube,
    video_path: Path,
    title: str,
    description: str,
    tags: list[str],
    category_id: str,
    privacy: str,
    publish_at: str | None,
) -> str:
    """Upload video using resumable upload. Returns the YouTube video URL."""
    if not video_path.exists():
        sys.exit(f"ERROR: Video file not found: {video_path}")

    if publish_at:
        status = {
            "privacyStatus": "private",
            "publishAt": publish_at,
            "selfDeclaredMadeForKids": False,
        }
    else:
        status = {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        }

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
        },
        "status": status,
    }

    media = MediaFileUpload(
        str(video_path),
        mimetype="video/*",
        resumable=True,
        chunksize=RESUMABLE_CHUNK_SIZE,
    )

    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    file_size_mb = video_path.stat().st_size / (1024 * 1024)
    print(f"Uploading: {video_path.name} ({file_size_mb:.1f} MB)")

    response = None
    while response is None:
        try:
            status_obj, response = request.next_chunk()
            if status_obj:
                pct = int(status_obj.progress() * 100)
                print(f"\rProgress: {pct}%  ", end="", flush=True)
        except HttpError as e:
            if e.resp.status in (500, 502, 503, 504):
                print(f"\nRetryable error {e.resp.status}, retrying...")
                continue
            raise

    print("\rProgress: 100%  ")
    return f"https://www.youtube.com/watch?v={response['id']}"


def post_comment(youtube, video_id: str, text: str) -> str | None:
    """Post a top-level comment on a video. Returns comment ID or None on failure."""
    try:
        resp = youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {"textOriginal": text}
                    },
                }
            },
        ).execute()
        return resp["id"]
    except HttpError as e:
        if e.resp.status == 403:
            print(f"[comment] 403 — re-register channel to add youtube.force-ssl scope: python3 scripts/upload_youtube.py --register")
        else:
            print(f"[comment] failed ({e.resp.status}): {e}")
        return None


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Upload a video to YouTube.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--register",
        action="store_true",
        help="Authenticate and register a new channel (run once per channel/account).",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all registered channels and exit.",
    )
    parser.add_argument(
        "--channel",
        default=None,
        help="Channel name (substring) or channel ID.",
    )
    parser.add_argument("--video", type=Path, help="Path to video file (mp4)")
    parser.add_argument("--title", help="Video title")
    parser.add_argument("--description", default="", help="Video description")
    parser.add_argument("--tags", default="", help="Comma-separated tags")
    parser.add_argument("--category", default="22", help="YouTube category ID (default: 22 = People & Blogs)")
    parser.add_argument(
        "--privacy",
        choices=["public", "private", "unlisted"],
        default="public",
        help="Privacy status (default: public). Ignored if --publish-at is set.",
    )
    parser.add_argument(
        "--publish-at",
        default=None,
        help="Schedule publish time in ISO 8601, e.g. '2026-03-28T18:00:00+05:30'.",
    )
    parser.add_argument("--slug", default=None, help="Optional content slug (for logging)")
    parser.add_argument(
        "--shorts",
        action="store_true",
        help="Mark as YouTube Short. Injects #Shorts into description. Video must be vertical (9:16).",
    )
    parser.add_argument(
        "--pin-longform-comment",
        action="store_true",
        help="After shorts upload, post a comment linking to long_form_url from metadata. Pin manually in Studio.",
    )
    args = parser.parse_args()

    load_dotenv(ENV_FILE)

    if args.register:
        register_channel()
        return

    if args.list:
        registry = load_registry()
        if not registry:
            print("No channels registered. Run with --register to add one.")
        else:
            print("Registered channels:")
            for cid, info in registry.items():
                handle = f"  {info.get('handle', '')}" if info.get("handle") else ""
                print(f"  • {info['name']}{handle}  ({cid})")
        return

    # Validate upload-required args
    if not args.video:
        parser.error("--video is required for upload")

    # Auto-load metadata from youtube_shorts_metadata.json when --shorts + --slug provided
    if args.shorts and args.slug and not args.title:
        date_str = args.slug[:10]
        week = get_iso_week(date_str)
        shorts_meta_path = BASE_DIR / "content" / "derivatives" / week / args.slug / "youtube_shorts_metadata.json"
        if shorts_meta_path.exists():
            raw_meta = json.loads(shorts_meta_path.read_text())
            long_form_url = ""

            m = re.search(r"short_(\d+)", str(args.video.name))
            idx = int(m.group(1)) if m else 0

            if isinstance(raw_meta, dict) and "shorts" in raw_meta:
                # Wrapper format: {"long_form_url": "...", "shorts": [...]}
                long_form_url = raw_meta.get("long_form_url", "")
                shorts_list = raw_meta["shorts"]
                if idx >= len(shorts_list):
                    sys.exit(
                        f"ERROR: No metadata for short_{idx:02d} — "
                        f"shorts array has {len(shorts_list)} entr{'y' if len(shorts_list)==1 else 'ies'} "
                        f"(indices 0–{len(shorts_list)-1}). Add an entry at index {idx}."
                    )
                meta = shorts_list[idx]
                print(f"Loaded Shorts metadata [index {idx}] from {shorts_meta_path.relative_to(BASE_DIR)}")

            elif isinstance(raw_meta, list):
                # Plain array format (no long_form_url).
                if idx >= len(raw_meta):
                    sys.exit(
                        f"ERROR: No metadata for short_{idx:02d} — "
                        f"array has {len(raw_meta)} entr{'y' if len(raw_meta)==1 else 'ies'} "
                        f"(indices 0–{len(raw_meta)-1}). Add an entry at index {idx}."
                    )
                meta = raw_meta[idx]
                print(f"Loaded Shorts metadata [index {idx}] from {shorts_meta_path.relative_to(BASE_DIR)}")

            else:
                # Legacy single-object — only valid for short_00.
                if idx > 0:
                    sys.exit(
                        f"ERROR: youtube_shorts_metadata.json is a single object but this is short_{idx:02d}. "
                        "Convert to wrapper format {\"long_form_url\": \"\", \"shorts\": [...]} so each short gets its own title."
                    )
                meta = raw_meta
                print(f"Loaded Shorts metadata from {shorts_meta_path.relative_to(BASE_DIR)}")

            args.title = args.title or meta.get("title", "")
            desc = args.description or meta.get("description", "")
            if long_form_url:
                desc = desc.rstrip() + f"\n\nFull video: {long_form_url}"
            args.description = desc
            if not args.tags and meta.get("tags"):
                args.tags = ",".join(meta["tags"])
            if long_form_url:
                print(f"Long-form URL injected: {long_form_url}")
            else:
                print("[info] long_form_url is empty — fill it in youtube_shorts_metadata.json after uploading the long-form.")
        else:
            print(f"[warn] No youtube_shorts_metadata.json for slug '{args.slug}' — using provided args")

    if not args.title:
        parser.error("--title is required for upload (or use --shorts --slug SLUG to auto-load)")

    # Inject #Shorts into description for Shorts uploads
    if args.shorts:
        if "#Shorts" not in args.description and "#shorts" not in args.description:
            args.description = args.description.rstrip() + "\n#Shorts"
        print("Mode: YouTube Short (#Shorts injected — ensure video is vertical 9:16)")

    if args.publish_at:
        try:
            datetime.fromisoformat(args.publish_at)
        except ValueError:
            sys.exit(
                f"ERROR: Invalid --publish-at format: '{args.publish_at}'\n"
                "Expected ISO 8601, e.g. '2026-03-28T18:00:00+05:30'"
            )

    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    video_path = args.video if args.video.is_absolute() else BASE_DIR / args.video

    channel = resolve_channel(args.channel)
    creds = get_credentials(channel["id"])
    youtube = build("youtube", "v3", credentials=creds)

    try:
        url = upload_video(
            youtube=youtube,
            video_path=video_path,
            title=args.title,
            description=args.description,
            tags=tags,
            category_id=args.category,
            privacy=args.privacy,
            publish_at=args.publish_at,
        )
    except HttpError as e:
        sys.exit(f"ERROR: YouTube API error during upload: {e}")

    # Normalise to short URL for cleaner storage
    video_id_m = re.search(r"[?&]v=([A-Za-z0-9_-]{11})", url)
    short_url = f"https://youtu.be/{video_id_m.group(1)}" if video_id_m else url

    print(f"\nUpload complete!")
    print(f"Channel:   {channel['name']} ({channel['id']})")
    print(f"Video URL: {short_url}")

    if args.publish_at:
        print(f"Scheduled: {args.publish_at}")
    else:
        print(f"Privacy:   {args.privacy}")

    if args.slug:
        print(f"Slug:      {args.slug}")

    # Auto-save long_form_url into shorts metadata after a non-shorts upload
    if args.slug and not args.shorts:
        date_str = args.slug[:10]
        week = get_iso_week(date_str)
        meta_path = BASE_DIR / "content" / "derivatives" / week / args.slug / "youtube_shorts_metadata.json"
        if meta_path.exists():
            try:
                meta = json.loads(meta_path.read_text())
                if isinstance(meta, dict):
                    meta["long_form_url"] = short_url
                    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
                    print(f"[meta] long_form_url saved → {meta_path.relative_to(BASE_DIR)}")
            except (json.JSONDecodeError, OSError) as e:
                print(f"[meta] WARNING: could not update long_form_url: {e}")

    # Post long-form link as comment on a short
    if args.shorts and args.pin_longform_comment:
        # Resolve long_form_url: from metadata file or already in description
        longform_url = ""
        if args.slug:
            date_str = args.slug[:10]
        week = get_iso_week(date_str)
        meta_path = BASE_DIR / "content" / "derivatives" / week / args.slug / "youtube_shorts_metadata.json"
            if meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text())
                    if isinstance(meta, dict):
                        longform_url = meta.get("long_form_url", "")
                except (json.JSONDecodeError, OSError):
                    pass

        if longform_url:
            video_id = video_id_m.group(1) if video_id_m else None
            if video_id:
                comment_text = f"Watch the full video: {longform_url}"
                comment_id = post_comment(youtube, video_id, comment_text)
                if comment_id:
                    print(f"[comment] posted → {comment_text}")
                    print(f"[comment] PIN manually in YouTube Studio → https://studio.youtube.com/video/{video_id}/comments")
        else:
            print("[comment] skipped — long_form_url empty in metadata (upload long-form first)")


if __name__ == "__main__":
    main()
