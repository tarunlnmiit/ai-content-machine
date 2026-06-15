"""Unit tests for lib.niche_config (centralized niche identity + model routing)."""
import pytest

from lib import niche_config as nc


@pytest.mark.unit
def test_niche_map_aliases_resolve_to_canonical():
    assert nc.NICHE_MAP["ds"] == "data_science_tech"
    assert nc.NICHE_MAP["life"] == "life_self_dev"
    assert nc.NICHE_MAP["poetry"] == "poetry_quotes"
    # canonical names map to themselves (idempotent)
    for canon in ("data_science_tech", "life_self_dev", "poetry_quotes"):
        assert nc.NICHE_MAP[canon] == canon


@pytest.mark.unit
def test_load_brand_base_has_expected_keys():
    expected = {
        "creator", "handle", "brand_name", "primary", "light", "dark_color",
        "light_bg", "dark_bg", "font_heading", "font_body", "font_style",
        "tone", "temperature", "label",
    }
    for niche in ("data_science_tech", "life_self_dev", "poetry_quotes"):
        assert set(nc.load_brand_base(niche)) == expected


@pytest.mark.unit
def test_model_for_routes_by_task():
    assert nc.model_for("hero_blog") == nc.OPUS
    assert nc.model_for("html_asset") == nc.SONNET
    assert nc.model_for("metadata") == nc.HAIKU
    # unknown task falls back to Sonnet
    assert nc.model_for("something_new") == nc.SONNET


@pytest.mark.unit
def test_ds_model_is_current_opus():
    _temps, models = nc.load_niche_config()
    assert models["data_science_tech"] == "claude-opus-4-8"
