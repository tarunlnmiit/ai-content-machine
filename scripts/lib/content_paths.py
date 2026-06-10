"""
Central path-construction module for content organization.
Ensures all path building respects ISO-week folder structure.
"""

from pathlib import Path
from .schedule_calc import get_iso_week

REPO = Path(__file__).parent.parent.parent


def blog_path(date_str: str, slug: str) -> Path:
	"""Path to a blog post markdown file. Slug should be full name like '2026-05-21_niche_slug'."""
	return REPO / "content" / "blogs" / get_iso_week(date_str) / f"{slug}.md"


def derivatives_dir(date_str: str, slug: str) -> Path:
	"""Path to a derivative content directory (contains schedule.json, metadata, etc.).
	Slug should be full name like '2026-05-21_niche_slug'."""
	return REPO / "content" / "derivatives" / get_iso_week(date_str) / slug


def raw_asset_path(date_str: str, filename: str) -> Path:
	"""Path to a raw asset file (MOV, etc.)."""
	return REPO / "assets" / "raw" / get_iso_week(date_str) / filename


def hyperframe_path(content_date_str: str, filename: str) -> Path:
	"""Path to a hyperframe video file. Groups by content date, not render date."""
	return REPO / "assets" / "hyperframes" / get_iso_week(content_date_str) / filename


def social_post_path(date_str: str, filename: str) -> Path:
	"""Path to a social media post image."""
	return REPO / "assets" / "social_posts" / get_iso_week(date_str) / filename


def carousel_path(date_str: str, filename: str) -> Path:
	"""Path to a carousel HTML or export file."""
	return REPO / "assets" / "carousels" / get_iso_week(date_str) / filename


def animation_path(date_str: str, filename: str) -> Path:
	"""Path to an output animation file (title card, lower third, outro)."""
	return REPO / "output" / "animations" / get_iso_week(date_str) / filename


def visual_path(date_str: str, filename: str) -> Path:
	"""Path to an output visual file (blog cover, etc.)."""
	return REPO / "output" / "visuals" / get_iso_week(date_str) / filename


def worksheet_path(date_str: str, filename: str) -> Path:
	"""Path to an output worksheet PDF."""
	return REPO / "output" / "worksheets" / get_iso_week(date_str) / filename


def captions_path(date_str: str, slug: str) -> Path:
	"""Path to captions JSON file in remotion."""
	return REPO / "remotion" / "public" / "captions" / get_iso_week(date_str) / f"{slug}.json"


def edit_plan_path(date_str: str, slug: str) -> Path:
	"""Path to edit plan JSON file in remotion."""
	return REPO / "remotion" / "public" / "edit-plans" / get_iso_week(date_str) / f"{slug}.json"


def remotion_videos_path(date_str: str, filename: str) -> Path:
	"""Path to source videos in remotion."""
	return REPO / "remotion" / "public" / "videos" / get_iso_week(date_str) / filename
