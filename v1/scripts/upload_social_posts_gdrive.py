#!/usr/bin/env python3
"""
Upload all social post PNGs to Google Drive and write fileIds to schedule.json.
Requires: gcloud CLI authenticated + googleapiclient installed.

Run: python3 scripts/upload_social_posts_gdrive.py
"""

import base64
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.auth.oauthlib.flow import InstalledAppFlow
from google.api_resources import build

REPO = Path(__file__).parent.parent
SCOPES = ['https://www.googleapis.com/auth/drive']

# GDrive folder IDs (from this session)
WEEK_FOLDERS = {
    "2026-W21": "1SlRADpNkDlw4YQpSg4mqvCcHz3bnFkfJ",
    "2026-W22": "10B_Q3rCwhpDwZzluaK1x9uliyQyjvK4r",
    "2026-W23": "1FCYpExo3Unlr4bz1JFcvdZGROw9zAEwt",
}


def get_drive_service():
    """Authenticate with Google Drive API."""
    creds = None
    token_file = REPO / ".gdrive_token.json"

    if token_file.exists():
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                REPO / ".gdrive_credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        token_file.write_text(creds.to_json())

    return build('drive', 'v3', credentials=creds)


def upload_file(service, filename, file_content_base64, parent_id):
    """Upload one PNG to GDrive."""
    file_body = {
        'name': filename,
        'parents': [parent_id],
    }

    # Decode base64 to bytes
    file_bytes = base64.b64decode(file_content_base64)

    file_obj = service.files().create(
        body=file_body,
        media_body=file_bytes,
        fields='id'
    ).execute()

    return file_obj['id']


def main():
    service = get_drive_service()

    # Load prep data
    prep_path = Path("/tmp/uploads.json")
    if not prep_path.exists():
        print("✗ /tmp/uploads.json not found. Run from main session first.")
        return

    data = json.loads(prep_path.read_text())

    # Upload each file, collect results
    # results structure: {slug: {platform: file_id}} plus {slug: {"_carousel_slides": {N: file_id}}}
    results: dict[str, dict] = {}
    file_weeks: dict[str, str] = {}  # slug → week (needed for path resolution)

    for fname, fdata in sorted(data.items()):
        week = fdata['week']
        b64 = fdata['base64']
        parent_id = WEEK_FOLDERS[week]

        # Carousel slide: {slug}_slide_{N}.png
        if "_slide_" in fname:
            slug_part, slide_rest = fname.rsplit("_slide_", 1)
            try:
                slide_n = int(slide_rest.replace(".png", ""))
            except ValueError:
                print(f"✗ {fname}: could not parse slide number")
                continue
            try:
                file_id = upload_file(service, fname, b64, parent_id)
                results.setdefault(slug_part, {}).setdefault("_carousel_slides", {})[slide_n] = file_id
                file_weeks[slug_part] = week
                print(f"✓ {slug_part} slide_{slide_n}: {file_id}")
            except Exception as e:
                print(f"✗ {slug_part} slide_{slide_n}: {e}")
            continue

        # Social image: {slug}_{platform}.png
        parts = fname.rsplit("_", 1)
        if len(parts) != 2:
            continue
        slug, platform = parts[0], parts[1].replace(".png", "")
        file_weeks[slug] = week

        try:
            file_id = upload_file(service, fname, b64, parent_id)
            results.setdefault(slug, {})[platform] = file_id
            print(f"✓ {slug} {platform}: {file_id}")
        except Exception as e:
            print(f"✗ {slug} {platform}: {e}")

    # Write results
    results_path = REPO / "output" / "gdrive_upload_results.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(json.dumps(results, indent=2))
    print(f"\n✓ Results saved to {results_path}")

    # Write image_urls + carousel_slide_urls to schedule.json files
    derivatives_root = REPO / "content" / "derivatives"
    updated = 0

    for slug, platforms in results.items():
        week = file_weeks.get(slug, "")
        sched_path = derivatives_root / week / slug / "schedule.json"
        if not sched_path.exists():
            continue

        sched_data = json.loads(sched_path.read_text())

        carousel_slides = platforms.pop("_carousel_slides", None)

        image_platforms = {k: v for k, v in platforms.items() if not k.startswith("_")}
        if image_platforms:
            sched_data["image_urls"] = {
                plat: f"https://drive.google.com/uc?export=view&id={fid}"
                for plat, fid in image_platforms.items()
            }

        if carousel_slides:
            ordered_ids = [carousel_slides[n] for n in sorted(carousel_slides)]
            sched_data["carousel_slide_urls"] = [
                f"https://drive.google.com/uc?export=view&id={fid}"
                for fid in ordered_ids
            ]

        sched_path.write_text(json.dumps(sched_data, indent=2))
        updated += 1
        print(f"✓ schedule.json {slug}")

    print(f"\n✓ Updated {updated} schedule.json files")


if __name__ == "__main__":
    main()
