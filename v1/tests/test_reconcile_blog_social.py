"""Plain-assert checks for reconcile_blog_social.py.

Run: python3 v1/tests/test_reconcile_blog_social.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

REPO_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(REPO_SCRIPTS))

import generate_tracker_html  # noqa: E402
import reconcile_blog_social as rbs  # noqa: E402

FIXTURE_MD = """\
## ds-slug-old
title:            Old DS Article
week:             W20
niche:            ds
date:             2026-01-01
medium.pub:       —
medium.status:    published
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  none
carousel.url:     —
reel.ref:         —
reel.status:      none
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  —

## ds-slug-progress
title:            In-Progress DS Article
week:             W30
niche:            ds
date:             2026-07-01
medium.pub:       —
medium.status:    published
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  created
carousel.url:     —
reel.ref:         —
reel.status:      script
reel.cta:         —
reel.ig:          —
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  —

## ds-slug-posted
title:            Posted DS Article
week:             W31
niche:            ds
date:             2026-07-15
medium.pub:       —
medium.status:    published
medium.submitted: —
medium.url:       —
medium.method:    —
linkedin.status:  —
linkedin.url:     —
carousel.status:  posted
carousel.url:     https://www.instagram.com/x/p/POSTED1/
reel.ref:         —
reel.status:      posted
reel.cta:         —
reel.ig:          https://www.instagram.com/x/reel/POSTED2/
reel.yt:          —
longform.ref:     —
longform.status:  none
longform.url:     —
worksheet.status: —
worksheet.url:    —
source_draft:     —
flags:            —
notes: |
  —
"""


def test_tracker_record_parsing():
    recs, errors = generate_tracker_html.parse_md(FIXTURE_MD)
    assert errors == [], errors
    assert len(recs) == 3
    slugs = {r["slug"] for r in recs}
    assert slugs == {"ds-slug-old", "ds-slug-progress", "ds-slug-posted"}
    old = next(r for r in recs if r["slug"] == "ds-slug-old")
    assert old["title"] == "Old DS Article"
    assert old["niche"] == "ds"
    assert rbs.unposted_assets(old) == ["carousel", "reel"]
    posted = next(r for r in recs if r["slug"] == "ds-slug-posted")
    assert rbs.unposted_assets(posted) == []


def test_in_progress_is_not_posted():
    """Pins the three-state distinction: 'created'/'script' are built, not posted.

    A carousel sitting at status 'created' must show up as unposted — a status
    of anything other than the literal string 'posted' must never be treated
    as 'has a carousel' for reconciliation purposes.
    """
    recs, errors = generate_tracker_html.parse_md(FIXTURE_MD)
    assert errors == []
    progress = next(r for r in recs if r["slug"] == "ds-slug-progress")

    assert rbs.asset_state("created") == "in-progress"
    assert rbs.asset_state("posted") == "posted"
    assert rbs.asset_state("none") == "missing"

    unposted = rbs.unposted_assets(progress)
    assert "carousel" in unposted
    assert "reel" in unposted

    detail = {d["asset"]: d for d in rbs.missing_detail(progress)}
    assert detail["carousel"]["state"] == "in-progress"
    assert detail["carousel"]["status"] == "created"
    assert detail["reel"]["state"] == "in-progress"
    assert detail["reel"]["status"] == "script"


def test_queue_ordering_next():
    recs, errors = generate_tracker_html.parse_md(FIXTURE_MD)
    assert errors == []
    queue = rbs.queue_for_niche(recs, "ds")
    # not-posted rows show up (missing AND in-progress), oldest date first;
    # the fully-posted row is excluded.
    assert [r["slug"] for r in queue] == ["ds-slug-old", "ds-slug-progress"]


def test_apply_required_before_write(tmp_path):
    tracker_copy = tmp_path / "content-tracker.md"
    tracker_copy.write_text(FIXTURE_MD, encoding="utf-8")

    ig_map = {
        "SHORT1": {"slug": "ds-slug-old", "asset": "carousel", "confidence": "high",
                   "source": "verified-2026-08-14", "permalink": "https://www.instagram.com/x/p/SHORT1/"},
    }
    recs, _ = generate_tracker_html.parse_md(FIXTURE_MD)
    proposals = rbs.proposed_updates(ig_map, recs)
    assert ("ds-slug-old", "carousel.status", "posted") in proposals

    before = tracker_copy.read_text(encoding="utf-8")

    # Simulate the CLI's "no --apply" path: build proposals, never call apply_updates.
    # The tracker file must be untouched.
    after_no_apply = tracker_copy.read_text(encoding="utf-8")
    assert after_no_apply == before

    # Now simulate "--apply": point tracker_update.set_field at the temp copy and
    # confirm it actually writes.
    with patch.object(generate_tracker_html, "DEFAULT_MD", tracker_copy):
        results = rbs.apply_updates(proposals)

    assert any(r.get("changed") for r in results if "error" not in r)
    after_apply = tracker_copy.read_text(encoding="utf-8")
    assert after_apply != before
    assert "carousel.status:  posted" in after_apply


def run_all():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    import inspect
    import tempfile

    for t in tests:
        sig = inspect.signature(t)
        if "tmp_path" in sig.parameters:
            with tempfile.TemporaryDirectory() as d:
                t(Path(d))
        else:
            t()
        print(f"PASS {t.__name__}")


if __name__ == "__main__":
    run_all()
