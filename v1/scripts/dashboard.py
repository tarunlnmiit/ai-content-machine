#!/usr/bin/env python3
"""
Local operator dashboard for the content pipeline.

Serves a static UI + JSON API on 127.0.0.1 only. Backend for the human
review/approve/kick-off-jobs loop: freshness checks, weekly menu toggling,
recording-session clip status, review approvals, and a small job runner
that shells out to existing pipeline scripts (allowlisted argv, no shell).

Auto-reloads on code change (re-execs in place; deferred while a job is running).

Run: python3 scripts/dashboard.py [--port 8765] [--no-reload]
"""

import argparse
import json
import os
import re
import subprocess
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

try:
    from lib.schedule_calc import get_iso_week
except Exception:
    def get_iso_week(date_str: str) -> str:
        d = datetime.fromisoformat(date_str).date()
        iso_year, iso_week, _ = d.isocalendar()
        return f"{iso_year}-W{iso_week:02d}"

# imported at module scope, not per-request, so --reload watches these files too
from lib.tracker_update import set_field, append_note, StaleValueError  # noqa: E402

HOST = "127.0.0.1"
DEFAULT_PORT = 8765
FRESH_DAYS = 7
LOG_MAX_LINES = 400
QID_RE = re.compile(r"^q\d{2}$")
THEME_RE = re.compile(r"[^a-z,-]")
VALID_NICHES = {"ds", "life", "poetry"}

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".mp4": "video/mp4",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".json": "application/json",
    ".md": "text/markdown; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
}


def today() -> str:
    return datetime.now().date().isoformat()


def current_week() -> str:
    """Active week = the week being prepped, not strictly today's.

    On Sundays the machine preps NEXT week, so a newer session folder
    (content/sessions/2026-W29/) outranks today's computed week. ISO week
    strings sort lexicographically, so max() is safe.
    """
    week = get_iso_week(today())
    sessions = REPO / "content" / "sessions"
    if sessions.is_dir():
        dirs = [d.name for d in sessions.iterdir()
                if d.is_dir() and re.fullmatch(r"\d{4}-W\d{2}", d.name)]
        if dirs:
            week = max([week, *dirs])
    return week


def is_fresh(date_str: str | None) -> bool:
    if not date_str:
        return False
    try:
        d = datetime.fromisoformat(date_str[:10]).date()
    except ValueError:
        return False
    return (datetime.now().date() - d).days <= FRESH_DAYS


# ---------------------------------------------------------------------------
# Job runner
# ---------------------------------------------------------------------------

class Job:
    def __init__(self, action: str, argv_batches: list[list[str]]):
        self.action = action
        self.argv_batches = argv_batches
        self.lines: list[str] = []
        self.running = True
        self.exit_code: int | None = None
        self.lock = threading.Lock()

    def append(self, line: str):
        with self.lock:
            self.lines.append(line)
            if len(self.lines) > LOG_MAX_LINES:
                self.lines = self.lines[-LOG_MAX_LINES:]

    def snapshot(self, since: int):
        with self.lock:
            lines = self.lines[since:]
            return lines, len(self.lines), self.running, self.exit_code


JOBS: dict[str, Job] = {}
JOBS_LOCK = threading.Lock()
TRACKER_LOCK = threading.Lock()  # Serialize tracker writes (read-modify-write)


def start_job(action: str, argv_batches: list[list[str]]) -> bool:
    """Returns False if that action is already running."""
    with JOBS_LOCK:
        existing = JOBS.get(action)
        if existing and existing.running:
            return False
        job = Job(action, argv_batches)
        JOBS[action] = job

    def run():
        exit_code = 0
        try:
            for argv in argv_batches:
                job.append(f"$ {' '.join(argv)}")
                proc = subprocess.Popen(
                    argv,
                    cwd=str(REPO),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
                for line in proc.stdout:
                    job.append(line.rstrip("\n"))
                proc.wait()
                exit_code = proc.returncode
                if exit_code != 0:
                    break
        except Exception as exc:
            job.append(f"[dashboard] job failed to launch: {exc}")
            exit_code = -1
        finally:
            with job.lock:
                job.exit_code = exit_code
                job.running = False

    threading.Thread(target=run, daemon=True).start()
    return True


def build_job_argv(action: str, params: dict) -> list[list[str]] | None:
    py = sys.executable
    week = current_week()

    if action == "analytics":
        return [[py, "scripts/collect_analytics.py"]]

    if action == "fetch_ideas":
        return [
            [py, "scripts/fetch_google_suggest.py"],
            [py, "scripts/fetch_external_feeds.py"],
        ]

    if action == "score":
        return [[py, "scripts/idea_scorer.py", "--force"]]

    if action == "pack":
        argv = [py, "scripts/generate_prompt_pack.py", "--force", "--week", current_week()]
        theme = params.get("theme")
        if theme:
            clean = THEME_RE.sub("", str(theme).lower())
            if clean:
                argv += ["--theme", clean]
        return [argv]

    if action == "menu":
        return [[py, "scripts/weekly_menu.py", "--week", current_week()]]

    if action == "slice":
        fname = params.get("file", "")
        if not fname or "/" in fname or ".." in fname:
            return None
        inbox = REPO / "assets" / "raw" / "inbox"
        if not (inbox / fname).exists():
            return None
        return [[py, "scripts/slice_raw_session.py", "--input",
                  f"assets/raw/inbox/{fname}", "--week", week]]

    if action == "composite":
        qid = params.get("qid", "")
        niche = params.get("niche", "")
        if not QID_RE.match(qid) or niche not in VALID_NICHES:
            return None
        return [[py, "scripts/composite_greenscreen.py", "--input",
                  f"content/sessions/{week}/clips/{qid}.mp4", "--niche", niche]]

    if action == "trim":
        qid = params.get("qid", "")
        niche = params.get("niche", "")
        if not QID_RE.match(qid) or niche not in VALID_NICHES:
            return None
        raw = f"content/sessions/{week}/clips/{qid}_composited.mp4"
        out = f"content/sessions/{week}/clips/{qid}_composited_trimmed.mp4"
        return [[py, "scripts/video_trim.py", "--raw", raw, "--niche", niche,
                  "--out", out]]

    if action == "episode":
        niche = params.get("niche", "")
        if niche not in VALID_NICHES:
            return None
        return [[py, "scripts/assemble_episode.py", "--week", week,
                  "--niche", niche]]

    return None


# ---------------------------------------------------------------------------
# State assembly (each piece must degrade gracefully, never raise)
# ---------------------------------------------------------------------------

def parse_menu(path: Path):
    if not path.exists():
        return {"exists": False, "sections": []}
    sections = []
    current = None
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return {"exists": True, "sections": []}
    for idx, line in enumerate(lines):
        if line.startswith("## "):
            current = {"title": line[3:].strip(), "items": []}
            sections.append(current)
            continue
        if line.startswith("- [ ]") or line.startswith("- [x]") or line.startswith("- [X]"):
            checked = line[3] in ("x", "X")
            text = line[5:].strip() if len(line) > 5 else ""
            text = re.sub(r"[*`]", "", text)  # strip md emphasis for display
            item = {"line_idx": idx, "checked": checked, "text": text}
            if current is None:
                current = {"title": "", "items": []}
                sections.append(current)
            current["items"].append(item)
    return {"exists": True, "sections": sections}


def parse_headline(path: Path):
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None
    in_summary = False
    for line in text.splitlines():
        if line.strip().startswith("## Summary"):
            in_summary = True
            continue
        if in_summary and line.strip().startswith("##"):
            break
        if in_summary and line.strip().startswith("-") and "**" in line:
            clean = re.sub(r"[*`]", "", line.strip().lstrip("- ").strip())
            # keep it a glanceable metric, not a paragraph
            m = re.search(r"\d[\d,–\-]*\s*(views|likes|subs(cribers)?|comments|reads|followers|saves)", clean, re.I)
            if m:
                end = clean.find(")", m.end())
                cut = end + 1 if 0 < end < m.end() + 60 else m.end()
                return clean[:max(cut, m.end())][:140]
            return clean[:140]
    return None


def parse_insights_date(path: Path):
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None
    m = re.search(r"\*Generated:\s*(\d{4}-\d{2}-\d{2})", text)
    if m:
        return m.group(1)
    try:
        return datetime.fromtimestamp(path.stat().st_mtime).date().isoformat()
    except Exception:
        return None


def newest_suggest_date(ideas_dir: Path):
    if not ideas_dir.exists():
        return None
    best = None
    for f in ideas_dir.glob("suggest_*.json"):
        m = re.match(r"suggest_(\d{4}-\d{2}-\d{2})\.json$", f.name)
        if m and (best is None or m.group(1) > best):
            best = m.group(1)
    return best


def scheduler_freshness(db_path: Path):
    if not db_path.exists():
        return {"date": None, "fresh": False}
    try:
        d = datetime.fromtimestamp(db_path.stat().st_mtime).date().isoformat()
    except Exception:
        return {"date": None, "fresh": False}
    return {"date": d, "fresh": is_fresh(d)}


def load_prompt_pack(week: str):
    path = REPO / "content" / "sessions" / week / "prompt_pack.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_session_manifest(week: str):
    path = REPO / "content" / "sessions" / week / "session_manifest.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def build_inbox():
    inbox = REPO / "assets" / "raw" / "inbox"
    if not inbox.exists():
        return []
    out = []
    try:
        for f in sorted(inbox.iterdir()):
            if not f.is_file():
                continue
            try:
                stat = f.stat()
            except OSError:
                continue
            out.append({
                "name": f.name,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            })
    except Exception:
        return []
    return out


def build_clips(week: str, manifest: dict | None, question_by_id: dict):
    if not manifest:
        return []
    clips_dir = REPO / "content" / "sessions" / week / "clips"
    out = []
    for c in manifest.get("clips", []):
        qid = c.get("qid", "")
        composited = (clips_dir / f"{qid}_composited.mp4").exists()
        trimmed = (
            (clips_dir / f"{qid}_composited_trimmed.mp4").exists()
            or (clips_dir / f"{qid}_trimmed.mp4").exists()
        )
        sliced = bool(c.get("clip")) and (clips_dir / f"{qid}.mp4").exists()
        q = question_by_id.get(qid, {})
        out.append({
            "qid": qid,
            "question": c.get("question"),
            "score": c.get("score"),
            "clip": c.get("clip"),
            "status": {
                "sliced": sliced,
                "composited": composited,
                "trimmed": trimmed,
            },
            "niche": q.get("niche"),
        })
    return out


def build_review(week: str):
    review_dir = REPO / "output" / "review" / week
    items = []
    episode_meta = {}
    approvals = {}
    approvals_path = review_dir / "approvals.json"
    if approvals_path.exists():
        try:
            approvals = json.loads(approvals_path.read_text(encoding="utf-8"))
        except Exception:
            approvals = {}

    if review_dir.exists():
        try:
            for f in sorted(review_dir.rglob("*")):
                if not f.is_file() or f.name == "approvals.json":
                    continue
                rel = f.relative_to(review_dir).as_posix()
                suffix = f.suffix.lower()
                if suffix == ".mp4":
                    kind = "video"
                elif suffix in (".png", ".jpg", ".jpeg"):
                    kind = "image"
                elif suffix in (".md", ".txt"):
                    kind = "meta"
                else:
                    continue
                entry = approvals.get(f.name) or approvals.get(rel)
                approved = entry.get("approved") if isinstance(entry, dict) else None
                items.append({
                    "name": f.name,
                    "rel_url": f"/review/{week}/{rel}",
                    "kind": kind,
                    "approved": approved,
                })
                if kind == "meta":
                    m = re.match(r"episode_(\w+)_meta\.md$", f.name)
                    if m:
                        try:
                            episode_meta[m.group(1)] = f.read_text(encoding="utf-8")
                        except Exception:
                            pass
        except Exception:
            pass

    return {"items": items, "episode_meta": episode_meta}


def build_jobs_status():
    out = {}
    with JOBS_LOCK:
        for action, job in JOBS.items():
            out[action] = {"running": job.running, "exit_code": job.exit_code}
    return out


def build_state() -> dict:
    week = current_week()

    headline = parse_headline(REPO / "data" / "analytics" / "weekly_insights.md")

    idea_date = newest_suggest_date(REPO / "data" / "ideas")
    insights_date = parse_insights_date(REPO / "data" / "analytics" / "weekly_insights.md")
    pack_path = REPO / "content" / "sessions" / week / "prompt_pack.json"

    menu = parse_menu(REPO / "data" / "ideas" / "weekly_menu.md")

    pack = load_prompt_pack(week)
    questions = pack.get("questions", []) if pack else []
    question_by_id = {q.get("id"): q for q in questions}

    manifest = load_session_manifest(week)
    unmatched = manifest.get("unmatched_questions", []) if manifest else []

    return {
        "week": week,
        "headline": headline,
        "freshness": {
            "idea_inputs": {"date": idea_date, "fresh": is_fresh(idea_date)},
            "insights": {"date": insights_date, "fresh": is_fresh(insights_date)},
            "prompt_pack": {"exists": pack_path.exists(), "week": week if pack_path.exists() else None},
            "scheduler": scheduler_freshness(REPO / "data" / "scheduling.db"),
        },
        "menu": menu,
        "questions": questions,
        "inbox": build_inbox(),
        "clips": build_clips(week, manifest, question_by_id),
        "unmatched_questions": unmatched,
        "review": build_review(week),
        "jobs": build_jobs_status(),
    }


# ---------------------------------------------------------------------------
# HTTP handler
# ---------------------------------------------------------------------------

def safe_join(base: Path, *parts: str) -> Path | None:
    """Resolve parts under base; return None if traversal escapes base."""
    try:
        candidate = base.joinpath(*parts).resolve()
        base_resolved = base.resolve()
        candidate.relative_to(base_resolved)
    except (ValueError, OSError):
        return None
    return candidate


class Handler(BaseHTTPRequestHandler):
    server_version = "ContentDashboard/1.0"

    def log_message(self, fmt, *args):
        pass  # keep stdout clean; errors still surface via response bodies

    def _send_json(self, obj, status=HTTPStatus.OK):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path: Path):
        ctype = CONTENT_TYPES.get(path.suffix.lower(), "application/octet-stream")
        try:
            data = path.read_bytes()
        except Exception:
            self._send_json({"error": "read failed"}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except Exception:
            return {}

    # -- routing -----------------------------------------------------------

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self._serve_static_index()
            return
        if path == "/favicon.ico":
            svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16">'
                   '<text y="13" font-size="13">🎙</text></svg>').encode()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "image/svg+xml")
            self.send_header("Content-Length", str(len(svg)))
            self.end_headers()
            self.wfile.write(svg)
            return
        if path == "/api/state":
            try:
                self._send_json(build_state())
            except Exception as exc:
                self._send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return
        if path == "/api/logs":
            self._handle_logs(parse_qs(parsed.query))
            return
        if path == "/tracker":
            self._serve_tracker()
            return
        if path.startswith("/review/"):
            self._serve_scoped(path, "/review/", REPO / "output" / "review")
            return
        if path.startswith("/sessions/"):
            self._serve_scoped(path, "/sessions/", REPO / "content" / "sessions")
            return

        self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/run":
            self._handle_run()
            return
        if path == "/api/menu-toggle":
            self._handle_menu_toggle()
            return
        if path == "/api/approve":
            self._handle_approve()
            return
        if path == "/api/tracker-field":
            self._handle_tracker_field()
            return
        if path == "/api/tracker-note":
            self._handle_tracker_note()
            return

        self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)

    # -- handlers ------------------------------------------------------------

    def _serve_tracker(self):
        html = REPO / "docs" / "content-tracker.html"
        if not html.exists():
            self._send_json({"error": "content-tracker.html not generated yet — run "
                                      "python3 scripts/generate_tracker_html.py"},
                            HTTPStatus.NOT_FOUND)
            return
        self._send_file(html)

    def _handle_tracker_field(self):
        """Set a single field in a tracker record via direct editing.

        Request: {slug, field, value, expected}
        Response: {slug, changed, field, old, new} or {error}
        """
        body = self._read_json_body()
        slug = (body.get("slug") or "").strip()
        field = (body.get("field") or "").strip()
        value = body.get("value", "")
        expected = body.get("expected")

        if not slug or not field:
            self._send_json({"error": "need slug and field"}, HTTPStatus.BAD_REQUEST)
            return

        try:
            with TRACKER_LOCK:
                result = set_field(slug, field, value, expected=expected)
                # Regenerate HTML after successful write
                if result.get("changed"):
                    subprocess.run(
                        [sys.executable, str(REPO / "scripts" / "generate_tracker_html.py")],
                        check=True, capture_output=True,
                    )
            self._send_json(result, HTTPStatus.OK)
        except KeyError:
            self._send_json({"error": f"slug {slug!r} not found"}, HTTPStatus.NOT_FOUND)
        except StaleValueError as exc:
            self._send_json({"error": str(exc), "current": exc.current}, HTTPStatus.CONFLICT)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except Exception as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def _handle_tracker_note(self):
        """Append a note to a tracker record.

        Request: {slug, text}
        Response: {slug, appended} or {error}
        """
        body = self._read_json_body()
        slug = (body.get("slug") or "").strip()
        text = (body.get("text") or "").strip()

        if not slug or not text:
            self._send_json({"error": "need slug and text"}, HTTPStatus.BAD_REQUEST)
            return

        try:
            with TRACKER_LOCK:
                result = append_note(slug, text)
                # Regenerate HTML after successful write
                subprocess.run(
                    [sys.executable, str(REPO / "scripts" / "generate_tracker_html.py")],
                    check=True, capture_output=True,
                )
            self._send_json(result, HTTPStatus.OK)
        except KeyError:
            self._send_json({"error": f"slug {slug!r} not found"}, HTTPStatus.NOT_FOUND)
        except Exception as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def _serve_static_index(self):
        index = REPO / "scripts" / "dashboard_static" / "index.html"
        if index.exists():
            self._send_file(index)
            return
        placeholder = (
            "<!doctype html><html><body>"
            "<h1>Content Dashboard</h1>"
            "<p>Static UI not built yet at scripts/dashboard_static/index.html.</p>"
            "<p>API is live at <a href='/api/state'>/api/state</a>.</p>"
            "</body></html>"
        ).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(placeholder)))
        self.end_headers()
        self.wfile.write(placeholder)

    def _serve_scoped(self, path: str, prefix: str, base: Path):
        rel = path[len(prefix):]
        if not rel:
            self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
            return
        parts = [p for p in rel.split("/") if p not in ("", ".")]
        if any(p == ".." for p in parts):
            self._send_json({"error": "invalid path"}, HTTPStatus.BAD_REQUEST)
            return
        target = safe_join(base, *parts)
        if target is None or not target.exists() or not target.is_file():
            self._send_json({"error": "not found"}, HTTPStatus.NOT_FOUND)
            return
        self._send_file(target)

    def _handle_logs(self, qs: dict):
        action = (qs.get("action") or [None])[0]
        since_raw = (qs.get("since") or ["0"])[0]
        try:
            since = int(since_raw)
        except ValueError:
            since = 0
        if not action:
            self._send_json({"error": "action required"}, HTTPStatus.BAD_REQUEST)
            return
        with JOBS_LOCK:
            job = JOBS.get(action)
        if job is None:
            self._send_json({"lines": [], "next": 0, "running": False, "exit_code": None})
            return
        lines, total, running, exit_code = job.snapshot(since)
        self._send_json({"lines": lines, "next": total, "running": running, "exit_code": exit_code})

    def _handle_run(self):
        body = self._read_json_body()
        action = body.get("action")
        params = body.get("params") or {}
        if not isinstance(action, str) or not isinstance(params, dict):
            self._send_json({"error": "bad request"}, HTTPStatus.BAD_REQUEST)
            return

        argv_batches = build_job_argv(action, params)
        if argv_batches is None:
            self._send_json({"error": "invalid action or params"}, HTTPStatus.BAD_REQUEST)
            return

        started = start_job(action, argv_batches)
        if not started:
            self._send_json({"error": "already running"}, HTTPStatus.CONFLICT)
            return
        self._send_json({"job": action})

    def _handle_menu_toggle(self):
        body = self._read_json_body()
        line_idx = body.get("line_idx")
        checked = body.get("checked")
        if not isinstance(line_idx, int) or not isinstance(checked, bool):
            self._send_json({"error": "bad request"}, HTTPStatus.BAD_REQUEST)
            return

        menu_path = REPO / "data" / "ideas" / "weekly_menu.md"
        if not menu_path.exists():
            self._send_json({"error": "menu not found"}, HTTPStatus.NOT_FOUND)
            return

        try:
            lines = menu_path.read_text(encoding="utf-8").splitlines(keepends=True)
        except Exception as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        if line_idx < 0 or line_idx >= len(lines):
            self._send_json({"error": "line_idx out of range"}, HTTPStatus.BAD_REQUEST)
            return

        line = lines[line_idx]
        stripped = line.lstrip()
        if not stripped.startswith("- ["):
            self._send_json({"error": "not a checkbox line"}, HTTPStatus.BAD_REQUEST)
            return

        indent = line[: len(line) - len(stripped)]
        rest = stripped[5:] if len(stripped) > 5 else ""
        newline_suffix = ""
        if rest.endswith("\r\n"):
            newline_suffix = ""  # rest already carries it
        mark = "x" if checked else " "
        lines[line_idx] = f"{indent}- [{mark}]{rest}"

        try:
            menu_path.write_text("".join(lines), encoding="utf-8")
        except Exception as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self._send_json({"ok": True})

    def _handle_approve(self):
        body = self._read_json_body()
        name = body.get("name")
        approved = body.get("approved", None)
        if not isinstance(name, str) or not name:
            self._send_json({"error": "bad request"}, HTTPStatus.BAD_REQUEST)
            return
        if approved is not None and not isinstance(approved, bool):
            self._send_json({"error": "bad request"}, HTTPStatus.BAD_REQUEST)
            return

        week = current_week()
        review_dir = REPO / "output" / "review" / week
        review_dir.mkdir(parents=True, exist_ok=True)
        approvals_path = review_dir / "approvals.json"

        data = {}
        if approvals_path.exists():
            try:
                data = json.loads(approvals_path.read_text(encoding="utf-8"))
            except Exception:
                data = {}

        if approved is None:
            data.pop(name, None)
        else:
            data[name] = {
                "approved": approved,
                "at": datetime.now(timezone.utc).isoformat(),
            }

        try:
            approvals_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        except Exception as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self._send_json({"ok": True})


def _reload_watch(interval: float = 1.0):
    """Re-exec when any already-imported script under scripts/ changes on disk.

    Jobs run in daemon threads, so exec would kill a composite or episode render
    mid-flight — a pending reload therefore waits until no job is running.
    """
    scripts_dir = REPO / "scripts"

    def watched() -> dict[Path, float]:
        seen: dict[Path, float] = {}
        for mod in list(sys.modules.values()):
            f = getattr(mod, "__file__", None)
            if not f:
                continue
            # __main__.__file__ is the path as typed on the command line, so it is
            # relative whenever the server was started that way — resolve before comparing.
            p = Path(f).resolve()
            if p.suffix == ".py" and p.is_relative_to(scripts_dir):
                try:
                    seen[p] = p.stat().st_mtime
                except OSError:
                    pass
        return seen

    known = watched()
    pending: set[str] = set()
    while True:
        time.sleep(interval)
        for path, mtime in watched().items():
            if known.get(path) not in (None, mtime):
                pending.add(path.name)
            known[path] = mtime
        if not pending:
            continue
        with JOBS_LOCK:
            busy = sorted(a for a, j in JOBS.items() if j.running)
        if busy:
            continue  # retry next tick; never kill a running job
        print(f"[reload] {', '.join(sorted(pending))} changed — restarting")
        sys.stdout.flush()
        os.execv(sys.executable, [sys.executable, *sys.argv])


def main():
    parser = argparse.ArgumentParser(description="Local content pipeline operator dashboard")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--no-reload", action="store_true",
                        help="don't restart when a script under scripts/ changes")
    args = parser.parse_args()

    server = ThreadingHTTPServer((HOST, args.port), Handler)
    reload_note = "" if args.no_reload else "  (auto-reload on code change)"
    print(f"Dashboard running at http://{HOST}:{args.port}{reload_note}", flush=True)
    if not args.no_reload:
        threading.Thread(target=_reload_watch, daemon=True).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
