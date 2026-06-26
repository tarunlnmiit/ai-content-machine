"""Tests for Medium SEO field extraction + interview parsing/assembly."""

from lib.seo import extract_seo, seo_manual_steps
from lib import interview


def test_extract_seo_parses_all_three_fields():
    md = (
        "# Title\n\n*Sub*\n\nBody.\n\n"
        "<!-- Medium tags: A, B -->\n"
        "<!-- Target keyphrase: data scientist portfolio 2026 -->\n"
        "<!-- SEO title: Data Scientist Portfolio 2026 -->\n"
        "<!-- SEO description: What hiring managers want in 2026. -->\n"
    )
    assert extract_seo(md) == {
        "keyphrase": "data scientist portfolio 2026",
        "seo_title": "Data Scientist Portfolio 2026",
        "seo_description": "What hiring managers want in 2026.",
    }


def test_extract_seo_is_tolerant_of_missing():
    assert extract_seo("no seo comments here") == {}
    assert extract_seo("") == {}


def test_seo_manual_steps_empty_when_no_fields():
    assert seo_manual_steps({}) == ""


def test_seo_manual_steps_includes_values():
    steps = seo_manual_steps({"seo_title": "T", "seo_description": "D", "keyphrase": "K"})
    assert "SEO title:        T" in steps
    assert "SEO description:  D" in steps
    assert "target keyphrase: K" in steps


def test_parse_article_captures_seo_fields():
    raw = (
        "TITLE OPTIONS: [FOMO] One | [FEAR] Two\n"
        "SUBTITLE: a subtitle\n"
        "ARTICLE:\n# One\nBody line.\n"
        "TAGS: tag1, tag2\n"
        "EMAIL CTA: Grab it.\n"
        "TARGET KEYPHRASE: morning routine that sticks\n"
        "SEO TITLE: Morning Routine That Sticks\n"
        "SEO DESCRIPTION: Build one that survives real life.\n"
    )
    p = interview._parse_article(raw)
    assert p["keyphrase"] == "morning routine that sticks"
    assert p["seo_title"] == "Morning Routine That Sticks"
    assert p["seo_description"] == "Build one that survives real life."
    # SEO header lines must not leak into the article body.
    assert "Body line." in p["article"]
    assert "TAGS" not in p["article"]
    assert "SEO TITLE" not in p["article"]


def test_assemble_markdown_appends_seo_comments_and_round_trips():
    parsed = {
        "title_options": ["Chosen Title"],
        "subtitle": "Sub",
        "article": "# Chosen Title\nBody.",
        "tags": ["tag1", "tag2"],
        "email_cta": "Grab it.",
        "keyphrase": "morning routine that sticks",
        "seo_title": "Morning Routine That Sticks",
        "seo_description": "Build one that survives real life.",
    }
    out = interview.assemble_markdown("Chosen Title", parsed)
    assert "<!-- Medium tags: tag1, tag2 -->" in out
    assert "<!-- Target keyphrase: morning routine that sticks -->" in out
    assert "<!-- SEO title: Morning Routine That Sticks -->" in out
    assert "<!-- SEO description: Build one that survives real life. -->" in out
    assert extract_seo(out) == {
        "keyphrase": "morning routine that sticks",
        "seo_title": "Morning Routine That Sticks",
        "seo_description": "Build one that survives real life.",
    }
