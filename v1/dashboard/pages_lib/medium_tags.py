from pathlib import Path

import streamlit as st

from pages_lib._common import copy_button

MEDIUM_TAGS: dict[str, list[str]] = {
    "Arts & Entertainment": [
        "Art", "Books", "Culture", "Design", "Fiction", "Food", "Humor",
        "Movies", "Music", "Photography", "Poetry", "Reading", "Short Story",
        "Social Media", "Sports", "Writing",
    ],
    "Industry": [
        "Business", "Entrepreneurship", "Finance", "Freelancing",
        "Investing", "Productivity", "Startup", "Venture Capital",
    ],
    "Innovation": ["Artificial Intelligence", "Science", "Space", "Technology"],
    "Life": [
        "Life", "Life Lessons", "Self-Improvement", "Creativity", "Health",
        "Love", "Mental Health", "Psychology", "Relationships", "Travel", "Inspiration",
    ],
    "Society": ["Education", "Future", "History", "Politics"],
    "Tech & Programming": [
        "Programming", "Python", "Data Science", "Data Analytics", "JavaScript", "Software Development",
        "UX", "Leadership", "AI", "AI Tools", "Developer Tools",
        "Claude", "Codex", "OpenAI",
    ],
}

MAX_TAGS = 5


def _slugify_tag(tag: str) -> str:
    return tag.lower().replace(" ", "-")


def render(repo: Path) -> None:
    st.title("🏷️ Medium Tag Picker")
    st.caption("Pick up to 5 tags → get a ready-to-run publish command.")

    st.markdown("---")

    # ── Blog file ────────────────────────────────────────────────────────────
    blogs_dir = repo / "content" / "blogs"
    blog_files = sorted(blogs_dir.glob("*.md")) if blogs_dir.exists() else []
    blog_names = [f.name for f in blog_files]

    if not blog_names:
        st.warning(f"No `.md` files found in `content/blogs/`")
        return

    selected_blog = st.selectbox("Blog file", blog_names)
    blog_path = f"content/blogs/{selected_blog}"

    # ── Niche schedule hint ──────────────────────────────────────────────────
    _SCHEDULE: dict[str, str] = {
        "life":    "Tuesday 2:00 PM IST",
        "poetry":  "Friday 3:00 PM IST",
        "data":    "Thursday 6:00 PM IST",
    }
    slug_lower = selected_blog.lower()
    publish_time = next(
        (v for k, v in _SCHEDULE.items() if k in slug_lower), None
    )
    if publish_time:
        st.info(f"⏰ Publish this post on **{publish_time}** — save as draft now, publish manually at that time.")

    # ── Publication + status ─────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        publication = st.text_input("Publication slug", value="humans-are-stories")
    with col2:
        status = st.selectbox("Status", ["draft", "public", "unlisted"])

    canonical_url = st.text_input(
        "Canonical URL (Substack live link)",
        placeholder="https://breathoflife.substack.com/p/...",
    )

    st.markdown("---")

    # ── Tag picker ───────────────────────────────────────────────────────────
    # Collect all current selections from session state to enforce max
    def _get_current_selections() -> list[str]:
        all_selected: list[str] = []
        for cat in MEDIUM_TAGS:
            key = f"pills_{cat}"
            val = st.session_state.get(key) or []
            all_selected.extend(val)
        return all_selected

    current = _get_current_selections()
    n = len(current)
    badge_color = "red" if n > MAX_TAGS else ("green" if n == MAX_TAGS else "blue")
    st.markdown(
        f"**Tags selected:** :{badge_color}[{n}/{MAX_TAGS}]"
        + (" — only first 5 will be used" if n > MAX_TAGS else "")
    )

    st.markdown("#### Available tags")
    for category, tags in MEDIUM_TAGS.items():
        st.pills(
            label=category,
            options=tags,
            selection_mode="multi",
            key=f"pills_{category}",
        )

    # ── Command builder ──────────────────────────────────────────────────────
    all_selected = _get_current_selections()
    final_tags = all_selected[:MAX_TAGS]

    if final_tags:
        st.markdown("---")
        st.markdown("#### Generated command")

        tags_str = ",".join(_slugify_tag(t) for t in final_tags)
        url_part = canonical_url.strip() if canonical_url.strip() else "<live-substack-url>"
        pub_part = f"--publication {publication}" if publication.strip() else ""

        cmd_lines = [
            f'python3 scripts/publish_medium.py \\',
            f'  --input "{blog_path}" \\',
            f'  --canonical-url {url_part} \\',
        ]
        if pub_part:
            cmd_lines.append(f"  {pub_part} \\")
        cmd_lines.append(f'  --tags "{tags_str}" \\')
        cmd_lines.append(f'  --status {status}')

        cmd = "\n".join(cmd_lines)
        st.code(cmd, language="bash")
        copy_button(cmd, key="copy_medium_cmd")
    else:
        st.markdown("---")
        st.info("Select at least one tag to generate the command.")
