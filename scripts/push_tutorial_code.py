#!/Users/tarungupta/miniconda3/envs/content_engine_env/bin/python3.14
"""
push_tutorial_code.py — Push a DS tutorial code file to GitHub and inject the URL
into the YouTube description for that content slug.

USAGE:
    python3 scripts/push_tutorial_code.py \\
        --tutorial-num 5 \\
        --date 2026-06-16 \\
        --slug "2026-06-16_data_science_tech_python-for-data-science-tutorial-5-out-of-10-for-visualizati" \\
        --title "Tutorial 5: Matplotlib + Seaborn"

WHAT IT DOES:
    1. Finds {ordinal}_script.ipynb (or .py) in ~/Desktop/Projects/python-course/
    2. Pushes the file to github.com/tarunlnmiit/machine_learning under
       python-for-data-science/tutorial-{N:02d}/
    3. Writes the permalink to content/derivatives/{week}/{slug}/github_code_url.txt
    4. Injects the GitHub link into youtube_metadata.json description,
       either replacing [LINKS_PLACEHOLDER] (if still present) or appending
       after the existing links block (idempotent via <!-- github-code --> marker)

AUTH:
    Requires `gh` CLI to be authenticated (gh auth login).
"""

import argparse
import base64
import json
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

sys.path.insert(0, str(Path(__file__).parent))
from lib.schedule_calc import get_iso_week
from lib.github_links import github_yt_description_snippet, has_github_snippet

SOURCE_DIR = Path.home() / "Desktop" / "Projects" / "python-course"
GITHUB_REPO = "tarunlnmiit/machine_learning"
REPO_SUBDIR = "python-for-data-science"

_ORDINALS = [
    "first", "second", "third", "fourth", "fifth",
    "sixth", "seventh", "eighth", "ninth", "tenth",
]


def _ordinal(n: int) -> str:
    if not 1 <= n <= len(_ORDINALS):
        raise ValueError(f"Tutorial number must be 1–{len(_ORDINALS)}, got {n}")
    return _ORDINALS[n - 1]


def find_tutorial_file(tutorial_num: int) -> Path:
    ordinal = _ordinal(tutorial_num)
    for ext in (".ipynb", ".py"):
        p = SOURCE_DIR / f"{ordinal}_script{ext}"
        if p.exists():
            return p
    raise FileNotFoundError(
        f"No code file found for tutorial {tutorial_num}. "
        f"Expected {SOURCE_DIR}/{ordinal}_script.ipynb or .py"
    )


def _gh_api(path: str, method: str = "GET", payload: dict | None = None) -> dict:
    """Call gh api and return parsed JSON. Raises RuntimeError on failure."""
    cmd = ["gh", "api", path]
    if method != "GET":
        cmd += ["--method", method]
    stdin_data = None
    if payload is not None:
        cmd += ["--input", "-"]
        stdin_data = json.dumps(payload)

    result = subprocess.run(cmd, input=stdin_data, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh api {method} {path} failed:\n{result.stderr.strip()}")
    return json.loads(result.stdout) if result.stdout.strip() else {}


def push_to_github(file_path: Path, tutorial_num: int, title: str) -> str:
    """Push file to GitHub repo. Returns the permalink URL to the file."""
    target_path = f"{REPO_SUBDIR}/tutorial-{tutorial_num:02d}/{file_path.name}"
    api_path = f"repos/{GITHUB_REPO}/contents/{target_path}"

    content_b64 = base64.b64encode(file_path.read_bytes()).decode()

    payload: dict = {
        "message": f"Add {title}",
        "content": content_b64,
    }

    # Check if file already exists (update needs the current sha)
    check = subprocess.run(
        ["gh", "api", api_path],
        capture_output=True, text=True
    )
    if check.returncode == 0:
        existing = json.loads(check.stdout)
        payload["sha"] = existing["sha"]
        payload["message"] = f"Update {title}"

    resp = _gh_api(api_path, method="PUT", payload=payload)
    html_url: str = resp["content"]["html_url"]
    return html_url


def write_url_file(date_str: str, slug: str, url: str) -> Path:
    """Write github_code_url.txt to the derivatives dir. Returns the file path."""
    week = get_iso_week(date_str)
    out_dir = BASE_DIR / "content" / "derivatives" / week / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    url_file = out_dir / "github_code_url.txt"
    url_file.write_text(url + "\n", encoding="utf-8")
    return url_file


def inject_into_yt_metadata(date_str: str, slug: str, url: str, title: str) -> bool:
    """Inject GitHub link into youtube_metadata.json description. Returns True if modified."""
    week = get_iso_week(date_str)
    yt_file = BASE_DIR / "content" / "derivatives" / week / slug / "youtube_metadata.json"
    if not yt_file.exists():
        return False

    data = json.loads(yt_file.read_text(encoding="utf-8"))
    desc: str = data.get("description", "")

    if has_github_snippet(desc):
        return False  # already injected

    snippet = github_yt_description_snippet(url, title)

    if "[LINKS_PLACEHOLDER]" in desc:
        # Replace placeholder — worksheet injection will add its block separately
        # Keep a placeholder so worksheet injection can still run after this
        combined = f"{snippet}\n\n[LINKS_PLACEHOLDER]"
        desc = desc.replace("[LINKS_PLACEHOLDER]", combined)
    else:
        # Append after existing links block
        desc = desc.rstrip("\n") + "\n\n" + snippet

    data["description"] = desc
    yt_file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Push a DS tutorial code file to GitHub and inject the URL into YT metadata.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--tutorial-num", type=int, required=True, help="Tutorial number (1–10)")
    parser.add_argument("--date", required=True, help="Content date YYYY-MM-DD")
    parser.add_argument("--slug", required=True, help="Full derivative slug (directory name)")
    parser.add_argument("--title", default=None, help="Tutorial title for commit message and description label")
    args = parser.parse_args()

    title = args.title or f"Tutorial {args.tutorial_num}"

    # 1. Find source file
    try:
        code_file = find_tutorial_file(args.tutorial_num)
    except (ValueError, FileNotFoundError) as e:
        sys.exit(f"ERROR: {e}")

    print(f"Source:  {code_file}")

    # 2. Push to GitHub
    print(f"Pushing to github.com/{GITHUB_REPO} ...")
    try:
        github_url = push_to_github(code_file, args.tutorial_num, title)
    except RuntimeError as e:
        sys.exit(f"ERROR: {e}")

    print(f"GitHub:  {github_url}")

    # 3. Write URL file
    url_file = write_url_file(args.date, args.slug, github_url)
    print(f"Written: {url_file.relative_to(BASE_DIR)}")

    # 4. Inject into youtube_metadata.json
    modified = inject_into_yt_metadata(args.date, args.slug, github_url, title)
    if modified:
        print("Injected GitHub link into youtube_metadata.json")
    else:
        print("[info] youtube_metadata.json already has GitHub link or not found — skipped")

    print("\nDone. Next steps:")
    print(f"  • Run inject_worksheet_ctas.py (if worksheet exists) — it will also pick up the GitHub URL")
    print(f"  • Run upload_youtube.py --slug {args.slug} — it will post the GitHub URL as a pinned comment")


if __name__ == "__main__":
    main()
