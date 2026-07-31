#!/usr/bin/env python3
"""Plain-assert tests for the listicle helpers in produce_blog.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from produce_blog import (
    LISTICLE_QUERY_RE, load_listicle_signals, extract_listicle_outline, _interleave,
    build_listicle_directive, build_listicle_question_directive,
)
import inspect
from lib import interview as _interview

# Listicle + interview combine: both interview calls must accept a directive.
assert "extra_instruction" in inspect.signature(_interview.generate_questions).parameters
assert "extra_instruction" in inspect.signature(_interview.write_article).parameters

# Call-1 directive must demand N discrete items, not one broad answer.
_q = build_listicle_question_directive(7)
assert "7" in _q and "DISTINCT" in _q and "Do NOT" in _q

# Call-2 directive is the same article-structure override the standard path uses.
_a = build_listicle_directive(7, "AI tools", "ds")
assert "Top 7" in _a and "## 1." in _a and "## 7." in _a
assert _q != _a, "question directive and article directive must not be the same string"

# 'skip' on creator input must be listicle-aware, not a generic angle.
from produce_blog import answer_on_behalf, get_creator_input
assert "listicle" in inspect.signature(answer_on_behalf).parameters
assert "listicle" in inspect.signature(get_creator_input).parameters

# _interleave: callers slice the head, so every group must be represented early.
_groups = [["a1", "a2", "a3", "a4"], ["b1", "b2"], [], ["c1", "c2", "c3"]]
assert _interleave(_groups) == ["a1", "b1", "c1", "a2", "b2", "c2", "a3", "c3", "a4"]
assert len({g[0] for g in _groups if g} - set(_interleave(_groups)[:3])) == 0, \
    "head of interleaved list must cover every non-empty group"
assert _interleave([]) == [] and _interleave([[], []]) == []

TRUE_CASES = [
    "best python IDEs 2026",
    "top 10 data science tools",
    "5 ways to learn SQL faster",
    "common mistakes beginners make",
    "alternatives to pandas",
    "4 productivity secrets I wish I knew",
    "6 steps to better focus",
    "the 2-minute rule for habits",
    "the 2-minute rule",
]
for q in TRUE_CASES:
    assert LISTICLE_QUERY_RE.search(q), f"expected match for: {q}"

FALSE_CASES = [
    "what is machine learning",
    "how does gradient descent work",
    "data science career path",
    "by the way I disagree",
    "a lesson I learned about grief",
]
for q in FALSE_CASES:
    assert not LISTICLE_QUERY_RE.search(q), f"expected no match for: {q}"

from datetime import date
from produce_blog import REPO

_today_artifact = REPO / "data" / "ideas" / f"listicle_trends_ds_{date.today().isoformat()}.json"
if not _today_artifact.exists():
    assert load_listicle_signals("ds", 7) is None

_LISTICLE_BLOG = """# Top 3 Things

Hook paragraph here.

## 1. First Item

First item body. It has a sentence.

## 2. Second Item

Second item body. It has a sentence too.

## 3. Third Item

Third item body. It has a sentence as well.

## Takeaway

The pattern that connects all three.

## CTA

Try this today. It will help.
"""

outline = extract_listicle_outline(_LISTICLE_BLOG, 3, "Top 3 Things")
assert outline is not None
outline_lines = outline.splitlines()
assert outline_lines[0].startswith("1. HOOK"), outline_lines[0]
assert "ITEM 1:" in outline and "ITEM 2:" in outline and "ITEM 3:" in outline
assert len(outline_lines) == 5, outline_lines

assert extract_listicle_outline(_LISTICLE_BLOG, 4, "Top 3 Things") is None

_NON_CONTIGUOUS_BLOG = """# Some List

## 1. First Item

Body one.

## 2. Second Item

Body two.

## 4. Fourth Item

Body four.
"""
assert extract_listicle_outline(_NON_CONTIGUOUS_BLOG, 3, "Some List") is None

print("OK")
