#!/usr/bin/env python3
"""
Find [IMAGE_INSERT: description | caption] markers in a blog .md file.
Search Pexels API for each, download best match, embed in Markdown.
Saves images to: content/blogs/{blog_stem}_images/{N:02d}_{section}_{slug}.jpg
Generates:        content/blogs/{blog_stem}_images/IMAGE_MAP.md
Replaces marker with: ![caption](path) + italic caption line

Marker format:
    [IMAGE_INSERT: search description]                   — description used for search + alt text
    [IMAGE_INSERT: search description | visible caption] — description for search, caption for display

Usage:
    # Auto-fetch from Pexels (all markers):
    python3 scripts/fetch_images.py --input content/blogs/BLOG.md

    # Preview markers without downloading:
    python3 scripts/fetch_images.py --input content/blogs/BLOG.md --dry-run

    # Embed your own image at marker N (1-indexed):
    python3 scripts/fetch_images.py --input content/blogs/BLOG.md --manual 2 --image path/to/your/photo.jpg

    # Embed your own image at marker N with custom caption:
    python3 scripts/fetch_images.py --input content/blogs/BLOG.md --manual 2 --image photo.jpg --alt "My caption"
"""

import argparse
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
from _console import console, progress_bar

REPO = Path(__file__).parent.parent
load_dotenv(REPO / ".env")

PEXELS_API   = "https://api.pexels.com/v1/search"
PIXABAY_API  = "https://pixabay.com/api/"
UNSPLASH_API = "https://api.unsplash.com/search/photos"
BLOGS_DIR    = REPO / "content" / "blogs"

# Matches [IMAGE_INSERT: description] or [IMAGE_INSERT: description | caption]
MARKER_RE = re.compile(r'\[IMAGE_INSERT:\s*([^\]|]+?)(?:\s*\|\s*([^\]]+))?\s*\]')


def get_pexels_key() -> str | None:
    return os.getenv("PEXELS_API_KEY")


def get_pixabay_key() -> str | None:
    return os.getenv("PIXABAY_API_KEY")


def get_unsplash_key() -> str | None:
    return os.getenv("UNSPLASH_ACCESS_KEY")


def _normalize_pexels(photo: dict) -> dict:
    return {
        "download_url": photo["src"]["large"],
        "page_url": photo.get("url", ""),
        "photographer": photo.get("photographer", "Pexels"),
        "source": "Pexels",
    }


def _normalize_pixabay(hit: dict) -> dict:
    return {
        "download_url": hit.get("largeImageURL", hit.get("webformatURL", "")),
        "page_url": hit.get("pageURL", ""),
        "photographer": hit.get("user", "Pixabay"),
        "source": "Pixabay",
    }


def _normalize_unsplash(photo: dict) -> dict:
    return {
        "download_url": photo["urls"]["regular"],
        "page_url": photo["links"]["html"],
        "photographer": photo["user"]["name"],
        "source": "Unsplash",
    }


def search_pexels(query: str, api_key: str) -> dict | None:
    """Return normalized photo dict or None."""
    try:
        resp = requests.get(
            PEXELS_API,
            headers={"Authorization": api_key},
            params={"query": query, "per_page": 5, "orientation": "landscape"},
            timeout=10,
        )
        resp.raise_for_status()
        photos = resp.json().get("photos", [])
        return _normalize_pexels(photos[0]) if photos else None
    except Exception as e:
        console.print(f"  [warn]Pexels search error for '{query}': {e}[/warn]")
        return None


def search_pixabay(query: str, api_key: str) -> dict | None:
    """Return normalized photo dict or None."""
    try:
        resp = requests.get(
            PIXABAY_API,
            params={
                "key": api_key,
                "q": query,
                "image_type": "photo",
                "orientation": "horizontal",
                "per_page": 5,
                "safesearch": "true",
            },
            timeout=10,
        )
        resp.raise_for_status()
        hits = resp.json().get("hits", [])
        return _normalize_pixabay(hits[0]) if hits else None
    except Exception as e:
        console.print(f"  [warn]Pixabay search error for '{query}': {e}[/warn]")
        return None


def search_unsplash(query: str, api_key: str) -> dict | None:
    """Return normalized photo dict or None."""
    try:
        resp = requests.get(
            UNSPLASH_API,
            headers={"Authorization": f"Client-ID {api_key}"},
            params={"query": query, "per_page": 5, "orientation": "landscape"},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return _normalize_unsplash(results[0]) if results else None
    except Exception as e:
        console.print(f"  [warn]Unsplash search error for '{query}': {e}[/warn]")
        return None


def find_photo(
    query: str,
    pexels_key: str | None,
    pixabay_key: str | None,
    unsplash_key: str | None,
) -> dict | None:
    """Try Pexels → Pixabay → Unsplash."""
    if pexels_key:
        photo = search_pexels(query, pexels_key)
        if photo:
            return photo
    if pixabay_key:
        photo = search_pixabay(query, pixabay_key)
        if photo:
            console.print(f"  [info]Pixabay fallback for: {query[:40]}[/info]")
            return photo
    if unsplash_key:
        photo = search_unsplash(query, unsplash_key)
        if photo:
            console.print(f"  [info]Unsplash fallback for: {query[:40]}[/info]")
            return photo
    return None


def download_image(photo: dict, dest_path: Path) -> bool:
    """Download image to dest_path using normalized photo dict."""
    url = photo["download_url"]
    try:
        resp = requests.get(url, timeout=30, stream=True)
        resp.raise_for_status()
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        console.print(f"  [warn]Download error: {e}[/warn]")
        return False


from lib.slug import slugify as _slugify

def slugify(text: str) -> str:
    return _slugify(text, max_length=50)


# Section labels inferred from marker position in document
_SECTION_ORDER = ["hook", "context", "section1", "section2", "section3", "section4", "takeaway"]

def infer_section(content: str, marker_full: str, marker_index: int, total: int) -> str:
    """Map 1-indexed marker to a section label based on rough position in document."""
    pos = content.find(marker_full)
    if pos == -1:
        return _SECTION_ORDER[min(marker_index - 1, len(_SECTION_ORDER) - 1)]
    fraction = pos / max(len(content), 1)
    # Map 0–1 fraction to section list
    idx = min(int(fraction * len(_SECTION_ORDER)), len(_SECTION_ORDER) - 1)
    return _SECTION_ORDER[idx]


def write_manifest(img_dir: Path, entries: list[dict], blog_path: Path) -> Path:
    """Write a Markdown manifest listing each image, section, description, and caption."""
    lines = [
        f"# Image Map — {blog_path.name}",
        "",
        "| # | File | Section | Search Description | Caption |",
        "|---|------|---------|-------------------|---------|",
    ]
    for e in entries:
        caption = e.get("caption") or "*(same as description)*"
        lines.append(
            f"| {e['n']} | `{e['filename']}` | {e['section']} | {e['desc']} | {caption} |"
        )
    lines += ["", f"Images folder: `{img_dir.relative_to(blog_path.parent)}/`"]
    manifest = img_dir / "IMAGE_MAP.md"
    manifest.write_text("\n".join(lines), encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Fetch Pexels images for [IMAGE_INSERT] markers in a blog.")
    parser.add_argument("--input",   required=True, help="Path to blog .md file")
    parser.add_argument("--dry-run", action="store_true", help="Show markers without downloading")
    parser.add_argument("--manual",  type=int, metavar="N", help="Embed your own image at marker N (1-indexed)")
    parser.add_argument("--image",   help="Path to your own image file (used with --manual)")
    parser.add_argument("--alt",     help="Alt text / caption for manual image (optional)")
    args = parser.parse_args()

    blog_path = Path(args.input)
    if not blog_path.is_absolute():
        blog_path = REPO / blog_path
    if not blog_path.exists():
        sys.exit(f"File not found: {blog_path}")

    content = blog_path.read_text(encoding="utf-8")
    # Each match: (description, caption) — caption may be empty string
    markers = MARKER_RE.findall(content)

    console.rule("[info]Image Fetcher[/info]")
    console.print(f"Blog: [bold]{blog_path.name}[/bold]")
    console.print(f"Markers found: {len(markers)}")

    if not markers:
        console.print("[success]No [IMAGE_INSERT] markers found — nothing to do.[/success]")
        return

    # ── Manual image embed ────────────────────────────────────────────────
    if args.manual is not None:
        if not args.image:
            sys.exit("--manual requires --image path/to/your/photo.jpg")

        n = args.manual
        if n < 1 or n > len(markers):
            sys.exit(f"--manual {n} out of range — blog has {len(markers)} marker(s)")

        img_path = Path(args.image)
        if not img_path.is_absolute():
            img_path = REPO / img_path
        if not img_path.exists():
            sys.exit(f"Image not found: {img_path}")

        desc_raw, cap_raw = markers[n - 1]
        desc_clean = desc_raw.strip()
        caption    = args.alt or cap_raw.strip() or desc_clean

        # Reconstruct original marker string for replacement
        marker_full = f"[IMAGE_INSERT: {desc_raw}" + (f" | {cap_raw}" if cap_raw.strip() else "") + "]"

        img_dir = blog_path.parent / f"{blog_path.stem}_images"
        img_dir.mkdir(parents=True, exist_ok=True)
        section = infer_section(content, marker_full, n, len(markers))
        dest = img_dir / f"{n:02d}_{section}_manual{img_path.suffix}"

        import shutil
        shutil.move(img_path, dest)

        rel_path    = dest.relative_to(REPO)
        replacement = f"![{caption}](/{rel_path})\n*{caption}*"

        updated = content.replace(marker_full, replacement, 1)
        blog_path.write_text(updated, encoding="utf-8")

        console.print(f"[success]✓ Marker {n} replaced with your image: {dest.name}[/success]")
        console.print(f"  Caption: {caption}")
        return

    if args.dry_run:
        console.print("\n[warn]Dry run — images not downloaded:[/warn]")
        for i, (desc, cap) in enumerate(markers, 1):
            cap_display = f" | {cap.strip()}" if cap.strip() else ""
            console.print(f"  {i}. {desc.strip()}{cap_display}")
        return

    pexels_key   = get_pexels_key()
    pixabay_key  = get_pixabay_key()
    unsplash_key = get_unsplash_key()
    if not pexels_key and not pixabay_key and not unsplash_key:
        sys.exit("No image API key set — need PEXELS_API_KEY, PIXABAY_API_KEY, or UNSPLASH_ACCESS_KEY in .env")

    img_dir = blog_path.parent / f"{blog_path.stem}_images"
    img_dir.mkdir(parents=True, exist_ok=True)

    replacements: list[tuple[str, str]] = []  # ordered (marker_full, replacement)
    manifest_entries = []
    photo_cache: dict[str, dict] = {}  # desc_clean → photo dict (skip duplicate API calls)

    with progress_bar() as progress:
        task = progress.add_task("Fetching images", total=len(markers))

        for i, (desc, cap) in enumerate(markers, 1):
            desc_clean = desc.strip()
            caption    = cap.strip() or desc_clean
            query      = desc_clean[:100]
            marker_full = f"[IMAGE_INSERT: {desc}" + (f" | {cap}" if cap.strip() else "") + "]"
            section    = infer_section(content, marker_full, i, len(markers))
            img_slug   = slugify(desc_clean)
            dest       = img_dir / f"{i:02d}_{section}_{img_slug}.jpg"

            progress.update(task, description=f"Searching: {query[:40]}")

            if desc_clean in photo_cache:
                photo = photo_cache[desc_clean]
                console.print(f"  [info]Reusing cached photo for: {query[:40]}[/info]")
            else:
                photo = find_photo(query, pexels_key, pixabay_key, unsplash_key)
                if photo:
                    photo_cache[desc_clean] = photo

            if not photo:
                console.print(f"  [warn]No photo found for: {query}[/warn]")
                manifest_entries.append({"n": i, "filename": "(not downloaded)", "section": section, "desc": desc_clean, "caption": caption})
                progress.advance(task)
                continue

            photographer = photo["photographer"]
            photo_url    = photo["page_url"]
            source       = photo["source"]

            progress.update(task, description=f"Downloading: {dest.name}")
            ok = download_image(photo, dest)

            if ok:
                rel_path = dest.relative_to(REPO)
                replacement = (
                    f"![{caption}](/{rel_path})\n"
                    f"*{caption} — Photo by [{photographer}]({photo_url}) on {source}*"
                )
                replacements.append((marker_full, replacement))
                manifest_entries.append({"n": i, "filename": dest.name, "section": section, "desc": desc_clean, "caption": caption})
                console.print(f"  [success]✓[/success] {dest.name}  [{caption}] ({source})")
            else:
                console.print(f"  [error]✗[/error] Failed to download for: {query}")
                manifest_entries.append({"n": i, "filename": "(download failed)", "section": section, "desc": desc_clean, "caption": caption})

            progress.advance(task)

    # Apply replacements in order — each .replace(..., 1) consumes the next occurrence
    updated = content
    for marker, replacement in replacements:
        updated = updated.replace(marker, replacement, 1)
    blog_path.write_text(updated, encoding="utf-8")

    manifest = write_manifest(img_dir, manifest_entries, blog_path)

    replaced = len(replacements)
    skipped  = len(markers) - replaced
    console.print(f"\n[success]✓ {replaced} image(s) embedded in {blog_path.name}[/success]")
    if skipped:
        console.print(f"  [warn]{skipped} marker(s) skipped (no Pexels result)[/warn]")
    console.print(f"  Images: {img_dir.relative_to(REPO)}/")
    console.print(f"  Map:    {manifest.relative_to(REPO)}")


if __name__ == "__main__":
    main()
