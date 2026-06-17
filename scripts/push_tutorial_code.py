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
STAGING_DIR = Path.home() / ".cache" / "content-machine" / "github_code_urls"

_ORDINALS = [
    "first", "second", "third", "fourth", "fifth",
    "sixth", "seventh", "eighth", "ninth", "tenth",
]

# All files to push with --all. (local_rel, repo_rel, tutorial_num or None)
_ALL_MANIFEST = [
    ("first_script.py",        "tutorial-01/first_script.py",         1),
    ("second_script.py",       "tutorial-02/second_script.py",        2),
    ("third_script.py",        "tutorial-03/third_script.py",         3),
    ("fourth_script.py",       "tutorial-04/fourth_script.py",        4),
    ("fourth_script.ipynb",    "tutorial-04/fourth_script.ipynb",     4),
    ("fifth_script.ipynb",     "tutorial-05/fifth_script.ipynb",      5),
    ("data/sales_records.csv", "data/sales_records.csv",              None),
    ("results.json",           "data/results.json",                   None),
    ("titanic_eda_dashboard.png", "tutorial-05/titanic_eda_dashboard.png", None),
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


def _push_file(file_path: Path, repo_target_path: str, commit_msg: str) -> str:
    """Low-level: push one file to GitHub. Returns permalink URL."""
    api_path = f"repos/{GITHUB_REPO}/contents/{REPO_SUBDIR}/{repo_target_path}"
    content_b64 = base64.b64encode(file_path.read_bytes()).decode()

    payload: dict = {"message": commit_msg, "content": content_b64}

    check = subprocess.run(["gh", "api", api_path], capture_output=True, text=True)
    if check.returncode == 0:
        payload["sha"] = json.loads(check.stdout)["sha"]
        payload["message"] = commit_msg.replace("Add ", "Update ")

    resp = _gh_api(api_path, method="PUT", payload=payload)
    return resp["content"]["html_url"]


def push_to_github(file_path: Path, tutorial_num: int, title: str) -> str:
    """Push a single tutorial file. Returns permalink URL."""
    repo_target = f"tutorial-{tutorial_num:02d}/{file_path.name}"
    return _push_file(file_path, repo_target, f"Add {title}")


def push_all() -> dict[int, str]:
    """Push all manifest files. Returns {tutorial_num: url} for tutorial files."""
    tutorial_urls: dict[int, str] = {}
    for local_rel, repo_rel, tnum in _ALL_MANIFEST:
        local_path = SOURCE_DIR / local_rel
        if not local_path.exists():
            print(f"  [skip] not found: {local_path}")
            continue
        label = f"Tutorial {tnum}" if tnum else repo_rel
        print(f"  Pushing {local_rel} ...", end=" ", flush=True)
        try:
            url = _push_file(local_path, repo_rel, f"Add python-for-data-science/{repo_rel}")
            print(url)
            if tnum and repo_rel.endswith((".py", ".ipynb")):
                # Keep only the first (primary) file URL per tutorial
                tutorial_urls.setdefault(tnum, url)
        except RuntimeError as e:
            print(f"FAILED: {e}")

    # Cache tutorial URLs for later use with update_yt_description.py
    if tutorial_urls:
        STAGING_DIR.mkdir(parents=True, exist_ok=True)
        for tnum, url in tutorial_urls.items():
            (STAGING_DIR / f"{tnum}.txt").write_text(url + "\n", encoding="utf-8")
        print(f"\nURLs cached to {STAGING_DIR}/")

    return tutorial_urls


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
        description="Push DS tutorial code to GitHub and inject URL into YT metadata.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--all", action="store_true", help="Push all tutorials 1–5 + data folder in one shot")
    parser.add_argument("--tutorial-num", type=int, help="Tutorial number (1–10) for single-file mode")
    parser.add_argument("--date", help="Content date YYYY-MM-DD (single-file mode)")
    parser.add_argument("--slug", help="Full derivative slug (single-file mode)")
    parser.add_argument("--title", default=None, help="Tutorial title for commit message and description label")
    args = parser.parse_args()

    if args.all:
        print(f"Pushing all files to github.com/{GITHUB_REPO}/{REPO_SUBDIR}/\n")
        tutorial_urls = push_all()
        print(f"\nDone. {len(tutorial_urls)} tutorial URLs cached.")
        print(f"Use update_yt_description.py to inject links into already-published videos.")
        return

    # Single-file mode
    if not args.tutorial_num:
        parser.error("--tutorial-num is required (or use --all)")
    if not args.date or not args.slug:
        parser.error("--date and --slug are required in single-file mode")

    title = args.title or f"Tutorial {args.tutorial_num}"

    try:
        code_file = find_tutorial_file(args.tutorial_num)
    except (ValueError, FileNotFoundError) as e:
        sys.exit(f"ERROR: {e}")

    print(f"Source:  {code_file}")
    print(f"Pushing to github.com/{GITHUB_REPO} ...")
    try:
        github_url = push_to_github(code_file, args.tutorial_num, title)
    except RuntimeError as e:
        sys.exit(f"ERROR: {e}")

    print(f"GitHub:  {github_url}")

    url_file = write_url_file(args.date, args.slug, github_url)
    print(f"Written: {url_file.relative_to(BASE_DIR)}")

    modified = inject_into_yt_metadata(args.date, args.slug, github_url, title)
    if modified:
        print("Injected GitHub link into youtube_metadata.json")
    else:
        print("[info] youtube_metadata.json already has GitHub link or not found — skipped")

    print(f"\nDone. Next steps:")
    print(f"  • Run inject_worksheet_ctas.py (if worksheet exists)")
    print(f"  • Run upload_youtube.py --slug {args.slug} — posts GitHub URL as pinned comment")


if __name__ == "__main__":
    main()
