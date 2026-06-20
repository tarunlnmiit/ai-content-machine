"""Unit tests for lib.virality — two-layer routing, compactness, project context."""
import pytest

from lib import virality as v


# ── routing ──────────────────────────────────────────────────────────────────
@pytest.mark.unit
@pytest.mark.parametrize("niche", ["poetry", "poetry_quotes", "life", "life_self_dev"])
def test_voice_niches_route_to_voice_layer(niche):
    block = v.virality_block("blog", niche)
    assert "AUTHENTICITY" in block
    assert "BUILD/TEACH" not in block
    assert "HONESTY" not in block          # tech-only guardrail
    # advisor: poetry/life omit the proof-over-claims tech framing (the phrase, not the word
    # "proof" — "Social Proof Inversion" is a valid voice hook name).
    assert "show on screen" not in block


@pytest.mark.unit
def test_ds_routes_to_tech_layer():
    block = v.virality_block("blog", "ds")
    assert "BUILD/TEACH" in block
    assert "HONESTY" in block
    assert "AUTHENTICITY" not in block


@pytest.mark.unit
def test_ds_without_project_omits_project_section():
    assert "PROJECT" not in v.virality_block("blog", "ds")


# ── project context ──────────────────────────────────────────────────────────
@pytest.mark.unit
def test_project_adds_pitch_and_keyword():
    block = v.virality_block("yt_script", "ds", project_key="autopilot")
    assert "PROJECT" in block
    assert "jobs" in block  # dm_keyword from projects.json


@pytest.mark.unit
def test_voice_niche_with_project_stays_voice():
    # Invariant: poetry/life never routed through the tech KB, even with --project.
    block = v.virality_block("blog", "poetry", project_key="autopilot")
    assert "AUTHENTICITY" in block          # voice layer
    assert "BUILD/TEACH" not in block       # not tech
    assert "PROJECT" in block               # project block still appends


@pytest.mark.unit
def test_load_project_unknown_is_none():
    assert v.load_project("does-not-exist") is None
    assert v.load_project(None) is None


# ── 5-beat gating ────────────────────────────────────────────────────────────
@pytest.mark.unit
def test_five_beat_only_for_short_content_types():
    assert "5-BEAT" not in v.virality_block("blog", "ds")
    assert "5-BEAT" in v.virality_block("scene_plan_short", "ds")
    assert "5-BEAT" in v.virality_block("clip_select", "poetry")


# ── always-present spine + CTA, and compactness ──────────────────────────────
@pytest.mark.unit
@pytest.mark.parametrize("niche", ["poetry", "life", "ds"])
def test_spine_and_cta_always_present(niche):
    block = v.virality_block("carousel", niche)
    assert "VIRALITY SPINE" in block
    assert "CTA" in block


@pytest.mark.unit
def test_block_is_compact():
    # Selective, not a KB dump — keep well under a few hundred words.
    block = v.virality_block("scene_plan_short", "ds", project_key="autopilot")
    assert len(block) < 1600


# ── hook filtering ───────────────────────────────────────────────────────────
@pytest.mark.unit
def test_voice_hooks_filter_by_niche():
    poetry = [c["name"] for c in v.load_voice_hooks("poetry")]
    ds = [c["name"] for c in v.load_voice_hooks("ds")]
    assert "Data / Mechanism Opener" in ds        # ds-only (use_for: ["ds"])
    assert "Data / Mechanism Opener" not in poetry


# ── graceful behaviour ───────────────────────────────────────────────────────
@pytest.mark.unit
def test_topic_multiplier_voice_vs_tech_triggers():
    # voice trigger lifts poetry; tech trigger does not lift poetry
    assert v.topic_virality_multiplier("Why nobody talks about loneliness", "poetry") > 1.0
    assert v.topic_virality_multiplier("Automate your MCP agent for free", "poetry") == 1.0
    # tech trigger lifts ds; plain title doesn't
    assert v.topic_virality_multiplier("5 free ways to automate Claude", "ds") > 1.0
    assert v.topic_virality_multiplier("Some general musings", "ds") == 1.0


@pytest.mark.unit
def test_topic_multiplier_past_performer_boost():
    base = v.topic_virality_multiplier("loneliness and grief", "poetry")
    boosted = v.topic_virality_multiplier("loneliness and grief", "poetry",
                                          past_keywords={"loneliness", "grief"})
    assert boosted > base


@pytest.mark.unit
def test_never_raises_returns_str():
    # Even for an unknown content_type / odd niche, returns a usable string.
    out = v.virality_block("unknown_type", "ds")
    assert isinstance(out, str) and "VIRALITY SPINE" in out


# ── per-niche caption formula injection (mavgpt + voice formulas) ─────────────
@pytest.mark.unit
def test_caption_formula_routes_per_niche():
    ds = v.virality_block("instagram_caption", "data_science_tech")
    life = v.virality_block("instagram_caption", "life_self_dev")
    poetry = v.virality_block("instagram_caption", "poetry_quotes")
    # DS gets mavgpt (caption-is-product); poetry/life never do.
    assert "KEYWORD" in ds and "caption IS the product" in ds
    assert "KEYWORD" not in poetry and "KEYWORD" not in life
    # Each niche carries its own formula, not another's.
    assert "mechanism line" in life
    assert "full poem verbatim" in poetry and "close on permission" in poetry
    assert "mechanism line" not in poetry


@pytest.mark.unit
def test_caption_formula_only_on_caption_content_types():
    # blog is not a caption content type → no caption formula injected.
    assert "CAPTION FORMULA" not in v.virality_block("blog", "data_science_tech")
    # shorts_caption is → mavgpt present for DS.
    assert "KEYWORD" in v.virality_block("shorts_caption", "data_science_tech")


@pytest.mark.unit
def test_caption_formula_digest_extracts_only_digest_section():
    d = v.caption_formula_digest("poetry_quotes")
    assert d and "forwarding mechanic" in d
    # Should NOT pull the long body (e.g. the reference-account header line).
    assert "Reference account" not in d
