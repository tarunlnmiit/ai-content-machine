#!/usr/bin/env python3
"""
Initialise data/scheduling.db with the posts table schema.
Safe to run multiple times — uses CREATE TABLE IF NOT EXISTS.
"""

import sqlite3
from pathlib import Path

REPO = Path(__file__).parent.parent
DB_PATH = REPO / "data" / "scheduling.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    platform          TEXT NOT NULL,          -- linkedin|instagram|facebook|threads
    content_text      TEXT,
    media_path        TEXT,
    scheduled_at      DATETIME NOT NULL,
    status            TEXT DEFAULT 'pending', -- pending|posted|failed|cancelled
    thread_parent_id  INTEGER,                -- legacy thread chaining (unused; kept for compat)
    metadata_json     TEXT,                   -- platform-specific extras (JSON string)
    slug              TEXT,                   -- which blog this came from
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    posted_at         DATETIME
);

CREATE INDEX IF NOT EXISTS idx_posts_status_scheduled
    ON posts (status, scheduled_at);

CREATE INDEX IF NOT EXISTS idx_posts_slug
    ON posts (slug);
"""


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
    print(f"DB ready: {DB_PATH.relative_to(REPO)}")

    # Show current row count if DB already existed
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    conn.close()
    print(f"Existing posts: {count}")


if __name__ == "__main__":
    main()
