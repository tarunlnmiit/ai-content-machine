#!/Users/tarungupta/miniconda3/envs/content_engine_env/bin/python3.14
"""
fetch_youtube_analytics.py — Pull YouTube channel performance data into the knowledge base.

FIRST TIME SETUP (run once per channel):
    python3 scripts/fetch_youtube_analytics.py --register
    → Opens a browser. Sign in with the Google account that owns the channel.
    → Repeat for each additional channel/account.

NORMAL USAGE:
    python3 scripts/fetch_youtube_analytics.py --channel "Breath of Life"
    python3 scripts/fetch_youtube_analytics.py          # interactive picker

OPTIONS:
    --register          Authenticate and register a new channel
    --list              List all registered channels
    --channel NAME|ID   Channel name (substring) or channel ID
    --days N            Lookback window in days (default: 90)
    --top-n N           Number of top videos to report (default: 25)
    --output PATH       Override output path for analytics markdown

OUTPUTS:
    data/analytics/youtube_analytics_<channel_name>.md
    data/kb/master_brief.md  (YouTube section appended/updated per channel)
"""

import argparse
import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
TOKEN_DIR = Path.home() / ".youtube-mcp"
CLIENT_SECRET = TOKEN_DIR / "client_secret.json"
REGISTRY_FILE = TOKEN_DIR / "channels.json"
ANALYTICS_DIR = BASE_DIR / "data" / "analytics"
KB_DIR = BASE_DIR / "data" / "kb"
ANALYTICS_CACHE = BASE_DIR / ".cache" / "analytics"  # gitignored
DEFAULT_CACHE_TTL_HOURS = 6


def _cache_fresh(path: Path, ttl_hours: float) -> bool:
    if not path.exists():
        return False
    return (time.time() - path.stat().st_mtime) / 3600 <= ttl_hours

# Full scope set — same across both scripts so one registered token works for both
ALL_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/youtube.upload",
]

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


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

    # If the account has multiple channels, pick which one to register
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

    # Save token under channel ID
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    token_path_for(channel["id"]).write_text(creds.to_json())

    # Update registry
    registry = load_registry()
    already_registered = channel["id"] in registry
    registry[channel["id"]] = {"name": channel["name"], "handle": channel["handle"]}
    save_registry(registry)

    action = "Updated" if already_registered else "Registered"
    print(f"\n{action}: {channel['name']}  ({channel['id']})")
    print(f"Token: {token_path_for(channel['id'])}")
    print("\nRegistered channels:")
    for cid, info in load_registry().items():
        print(f"  • {info['name']}  ({cid})")


# ── Channel resolution ────────────────────────────────────────────────────────
def resolve_channel(channel_hint: str | None) -> dict:
    """
    Return {id, name, handle} from the registry.
    No API call — uses locally stored registry only.
    """
    registry = load_registry()

    if not registry:
        sys.exit(
            "No channels registered yet.\n"
            "Run:  python3 scripts/fetch_youtube_analytics.py --register"
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

    # Interactive menu
    print("\nRegistered YouTube channels:")
    for i, ch in enumerate(channels, 1):
        handle = f"  {ch.get('handle', '')}" if ch.get("handle") else ""
        print(f"  [{i}] {ch['name']}{handle}  ({ch['id']})")

    while True:
        raw = input(f"\nSelect channel [1-{len(channels)}]: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(channels):
            ch = channels[int(raw) - 1]
            print(f"Selected: {ch['name']} ({ch['id']})")
            print(f"Tip: use --channel \"{ch['name']}\" to skip this prompt next time.")
            return ch
        print(f"Please enter a number between 1 and {len(channels)}.")


# ── YouTube Data API helpers ──────────────────────────────────────────────────
def get_video_ids_in_window(youtube, channel_id: str, days: int) -> list[dict]:
    """Return list of {id, title, publishedAt} for videos uploaded in last `days` days."""
    published_after = (datetime.now(timezone.utc) - timedelta(days=days)).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
    video_ids = []
    page_token = None

    while True:
        resp = youtube.search().list(
            part="id",
            channelId=channel_id,
            type="video",
            publishedAfter=published_after,
            maxResults=50,
            pageToken=page_token,
            order="date",
        ).execute()

        for item in resp.get("items", []):
            video_ids.append(item["id"]["videoId"])

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    if not video_ids:
        return []

    videos = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i : i + 50]
        resp = youtube.videos().list(part="snippet", id=",".join(batch)).execute()
        for item in resp.get("items", []):
            videos.append({
                "id": item["id"],
                "title": item["snippet"]["title"],
                "publishedAt": item["snippet"]["publishedAt"],
            })

    return videos


# ── YouTube Analytics API helpers ─────────────────────────────────────────────
def get_video_metrics(yt_analytics, channel_id: str, video_ids: list[str], days: int) -> dict:
    end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    results = {}
    for i in range(0, len(video_ids), 200):
        batch = video_ids[i : i + 200]
        video_filter = f"channel=={channel_id};video=={','.join(batch)}"
        try:
            resp = yt_analytics.reports().query(
                ids=f"channel=={channel_id}",
                startDate=start_date,
                endDate=end_date,
                metrics="estimatedMinutesWatched,views,averageViewDuration,averageViewPercentage,subscribersGained",
                dimensions="video",
                filters=video_filter,
                maxResults=200,
            ).execute()
        except HttpError as e:
            print(f"Warning: Analytics API error for batch {i}: {e}")
            continue

        headers = [col["name"] for col in resp.get("columnHeaders", [])]
        for row in resp.get("rows", []):
            record = dict(zip(headers, row))
            vid = record.get("video")
            if vid:
                results[vid] = record

    return results


def get_dayofweek_performance(yt_analytics, channel_id: str, days: int) -> dict:
    """Fetch daily views then aggregate by weekday (Mon–Sun)."""
    end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    try:
        resp = yt_analytics.reports().query(
            ids=f"channel=={channel_id}",
            startDate=start_date,
            endDate=end_date,
            metrics="views",
            dimensions="day",
            maxResults=days + 5,
        ).execute()
    except HttpError as e:
        print(f"Warning: day-of-week query failed: {e}")
        return {}

    totals = {d: 0 for d in DAYS_OF_WEEK}
    counts = {d: 0 for d in DAYS_OF_WEEK}
    for row in resp.get("rows", []):
        date_str, views = row[0], int(row[1])
        weekday_name = datetime.strptime(date_str, "%Y-%m-%d").strftime("%A")
        if weekday_name in totals:
            totals[weekday_name] += views
            counts[weekday_name] += 1

    return {
        day: round(totals[day] / counts[day]) if counts[day] else 0
        for day in DAYS_OF_WEEK
    }


def get_subscriber_drivers(yt_analytics, channel_id: str, video_ids: list[str], days: int, top_n: int = 5) -> list[dict]:
    end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    if not video_ids:
        return []

    video_filter = f"channel=={channel_id};video=={','.join(video_ids[:200])}"
    try:
        resp = yt_analytics.reports().query(
            ids=f"channel=={channel_id}",
            startDate=start_date,
            endDate=end_date,
            metrics="subscribersGained,views",
            dimensions="video",
            filters=video_filter,
            sort="-subscribersGained",
            maxResults=top_n,
        ).execute()
    except HttpError as e:
        print(f"Warning: subscriber drivers query failed: {e}")
        return []

    headers = [col["name"] for col in resp.get("columnHeaders", [])]
    return [dict(zip(headers, row)) for row in resp.get("rows", [])]


def get_avg_dropoff(yt_analytics, channel_id: str, video_ids: list[str], n: int = 20) -> float | None:
    end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    start_date = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%d")

    recent_ids = video_ids[:n]
    if not recent_ids:
        return None

    video_filter = f"channel=={channel_id};video=={','.join(recent_ids)}"
    try:
        resp = yt_analytics.reports().query(
            ids=f"channel=={channel_id}",
            startDate=start_date,
            endDate=end_date,
            metrics="averageViewPercentage",
            dimensions="video",
            filters=video_filter,
            maxResults=n,
        ).execute()
    except HttpError as e:
        print(f"Warning: drop-off query failed: {e}")
        return None

    rows = resp.get("rows", [])
    percentages = [row[1] for row in rows if row[1] is not None]
    return round(sum(percentages) / len(percentages), 1) if percentages else None


# ── Formatting ────────────────────────────────────────────────────────────────
def fmt_duration(seconds: float) -> str:
    if not seconds:
        return "—"
    m, s = divmod(int(seconds), 60)
    return f"{m}m {s:02d}s"


def fmt_watch_time(minutes: float) -> str:
    if not minutes:
        return "—"
    hrs = minutes / 60
    return f"{hrs:,.1f}h" if hrs >= 1 else f"{int(minutes)}m"


# ── Report builder ────────────────────────────────────────────────────────────
def build_report(
    channel_name: str,
    videos: list[dict],
    metrics: dict,
    dayofweek: dict,
    subscriber_drivers: list[dict],
    avg_dropoff: float | None,
    top_n: int,
    days: int,
) -> str:
    today = datetime.now().strftime("%Y-%m-%d")

    def watch_time_key(v):
        return metrics.get(v["id"], {}).get("estimatedMinutesWatched", 0) or 0

    sorted_videos = sorted(videos, key=watch_time_key, reverse=True)[:top_n]

    lines = [
        f"# YouTube Analytics — {channel_name}",
        f"*{today} | Last {days} days | Top {top_n} videos by watch time*",
        "",
        f"## Top {top_n} Videos by Watch Time",
        "",
        "| Rank | Title | Views | Watch Time | Avg Duration | Retention |",
        "|------|-------|------:|-----------|-------------:|----------:|",
    ]

    for rank, v in enumerate(sorted_videos, 1):
        m = metrics.get(v["id"], {})
        title = v["title"][:52] + "..." if len(v["title"]) > 55 else v["title"]
        views = f"{int(m.get('views', 0) or 0):,}"
        wt = fmt_watch_time(m.get("estimatedMinutesWatched", 0))
        dur = fmt_duration(m.get("averageViewDuration", 0))
        ret = f"{m.get('averageViewPercentage', 0) or 0:.1f}%" if m.get("averageViewPercentage") else "—"
        lines.append(f"| {rank} | {title} | {views} | {wt} | {dur} | {ret} |")

    lines += [
        "",
        "## Avg Daily Views by Day of Week",
        "",
        "| Day | Avg Daily Views |",
        "|-----|----------------:|",
    ]
    for day in DAYS_OF_WEEK:
        lines.append(f"| {day} | {dayofweek.get(day, 0):,} |")

    if subscriber_drivers:
        lines += [
            "",
            "## Top Subscriber Drivers",
            "",
            "| Title | New Subscribers | Views |",
            "|-------|----------------:|------:|",
        ]
        id_to_title = {v["id"]: v["title"] for v in videos}
        for row in subscriber_drivers:
            vid = row.get("video", "")
            title = id_to_title.get(vid, vid)
            title = title[:52] + "..." if len(title) > 55 else title
            lines.append(
                f"| {title} | {int(row.get('subscribersGained', 0) or 0):,} | {int(row.get('views', 0) or 0):,} |"
            )

    lines += ["", "## Average Drop-off Point (Last 20 Videos)", ""]
    if avg_dropoff is not None:
        lines.append(f"Viewers watch an average of **{avg_dropoff}%** of each video before dropping off.")
    else:
        lines.append("No retention data available.")

    lines.append("")
    return "\n".join(lines)


def update_master_brief(kb_dir: Path, channel_name: str, youtube_section: str) -> None:
    """Insert/replace the ## YouTube Analytics — <channel> section in master_brief.md."""
    brief_path = kb_dir / "master_brief.md"
    section_header = f"## YouTube Analytics — {channel_name}"

    content = brief_path.read_text() if brief_path.exists() else "# Master Brief\n\n"

    if section_header in content:
        start = content.index(section_header)
        next_section = content.find("\n## ", start + len(section_header))
        if next_section == -1:
            content = content[:start] + youtube_section.strip() + "\n"
        else:
            content = content[:start] + youtube_section.strip() + "\n\n" + content[next_section + 1:]
    else:
        content = content.rstrip() + "\n\n" + youtube_section.strip() + "\n"

    brief_path.write_text(content)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Fetch YouTube analytics into the knowledge base.",
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
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument("--top-n", type=int, default=25)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Bypass the API-response cache and fetch fresh data.",
    )
    parser.add_argument(
        "--cache-ttl-hours",
        type=float,
        default=DEFAULT_CACHE_TTL_HOURS,
        help=f"Cached API data is reused if younger than this (default {DEFAULT_CACHE_TTL_HOURS}h).",
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

    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    KB_DIR.mkdir(parents=True, exist_ok=True)

    channel = resolve_channel(args.channel)
    channel_id = channel["id"]
    channel_name = channel["name"]

    safe_name = "".join(c if c.isalnum() or c in "-_ " else "" for c in channel_name).strip().replace(" ", "_")
    output_path = args.output or (ANALYTICS_DIR / f"youtube_analytics_{safe_name}.md")

    cache_file = ANALYTICS_CACHE / f"youtube_{channel_id}_{args.days}.json"
    data = None
    if not args.refresh and _cache_fresh(cache_file, args.cache_ttl_hours):
        data = json.loads(cache_file.read_text())
        print(f"[cache hit] reusing API data from {cache_file.name} (--refresh to bypass)")

    if data is None:
        creds = get_credentials(channel_id)
        youtube = build("youtube", "v3", credentials=creds)
        yt_analytics = build("youtubeAnalytics", "v2", credentials=creds)

        print(f"Fetching videos uploaded in last {args.days} days...")
        videos = get_video_ids_in_window(youtube, channel_id, args.days)
        print(f"Found {len(videos)} videos.")

        if not videos:
            print("No videos found in this window. Exiting.")
            return

        video_ids = [v["id"] for v in videos]

        print("Fetching per-video analytics metrics...")
        metrics = get_video_metrics(yt_analytics, channel_id, video_ids, args.days)

        print("Fetching day-of-week performance...")
        dayofweek = get_dayofweek_performance(yt_analytics, channel_id, args.days)

        print("Fetching top subscriber drivers...")
        sub_drivers = get_subscriber_drivers(yt_analytics, channel_id, video_ids, args.days)

        print("Fetching average drop-off (last 20 videos)...")
        avg_dropoff = get_avg_dropoff(yt_analytics, channel_id, video_ids)

        data = {
            "videos": videos,
            "metrics": metrics,
            "dayofweek": dayofweek,
            "sub_drivers": sub_drivers,
            "avg_dropoff": avg_dropoff,
        }
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps(data))

    videos = data["videos"]
    metrics = data["metrics"]
    dayofweek = data["dayofweek"]
    sub_drivers = data["sub_drivers"]
    avg_dropoff = data["avg_dropoff"]

    if not videos:
        print("No videos found in this window. Exiting.")
        return

    print("Building report...")
    report = build_report(channel_name, videos, metrics, dayofweek, sub_drivers, avg_dropoff, args.top_n, args.days)

    output_path.write_text(report)
    print(f"Analytics written to: {output_path}")

    today = datetime.now().strftime("%Y-%m-%d")
    youtube_section = (
        f"## YouTube Analytics — {channel_name}\n\n"
        f"*Updated {today} — full report at data/analytics/youtube_analytics_{safe_name}.md*\n\n"
    )

    def watch_time_key(v):
        return metrics.get(v["id"], {}).get("estimatedMinutesWatched", 0) or 0

    top5 = sorted(videos, key=watch_time_key, reverse=True)[:5]
    youtube_section += "**Top 5 Videos by Watch Time:**\n"
    for rank, v in enumerate(top5, 1):
        m = metrics.get(v["id"], {})
        wt = fmt_watch_time(m.get("estimatedMinutesWatched", 0))
        ret = f"{m.get('averageViewPercentage', 0) or 0:.1f}%" if m.get("averageViewPercentage") else "—"
        youtube_section += f"{rank}. {v['title']} — {wt} watch time, {ret} retention\n"

    if avg_dropoff:
        youtube_section += f"\n**Avg retention:** {avg_dropoff}% through video\n"

    update_master_brief(KB_DIR, channel_name, youtube_section)
    print(f"master_brief.md updated: {KB_DIR / 'master_brief.md'}")


if __name__ == "__main__":
    main()
