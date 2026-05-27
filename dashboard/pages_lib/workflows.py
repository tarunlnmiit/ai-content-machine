"""Workflows — trigger scripts via UI."""

from pathlib import Path

import streamlit as st

from ._common import NICHES, NICHE_LABELS, py_cmd, run_cmd, show_run_result


WORKFLOWS = {
    "daily_ideas": {
        "label": "🔄 Daily Ideas Refresh",
        "desc": "Reddit + YT + external + suggest + scorer + Notion (~5 min)",
    },
    "produce_blog": {
        "label": "✍️ Produce Blog from Topic",
        "desc": "Generate full blog markdown from a topic string",
    },
    "ghostwrite": {
        "label": "👻 Ghostwrite from Notes",
        "desc": "Convert notes/transcript → blog in your voice",
    },
    "fetch_images": {
        "label": "🖼️ Fetch Blog Images",
        "desc": "Pexels images per blog content",
    },
    "fetch_videos": {
        "label": "🎥 Fetch B-roll Videos",
        "desc": "Pexels/Pixabay clips from script [BROLL:] cues",
    },
    "repurpose_blog": {
        "label": "♻️ Repurpose Blog → Derivatives",
        "desc": "Twitter thread, LinkedIn, IG, Threads, newsletter",
    },
    "generate_design": {
        "label": "🎨 Claude Design Prompts",
        "desc": "Slides + reel covers + social posts prompts",
    },
    "auto_edit": {
        "label": "🎬 Auto-edit Long-form",
        "desc": "Whisper + broll overlay + captions",
    },
    "clip_shorts": {
        "label": "📱 Generate Shorts",
        "desc": "Cut long-form → 3-5 vertical clips w/ captions",
    },
    "upload_youtube": {
        "label": "📤 Upload to YouTube",
        "desc": "Long-form or shorts upload",
    },
    "publish_medium": {
        "label": "📰 Publish to Medium",
        "desc": "Push blog to Medium w/ canonical URL",
    },
    "load_posts": {
        "label": "📅 Load Posts → Scheduler DB",
        "desc": "Insert derivatives into scheduling.db",
    },
    "sync_notion": {
        "label": "🔗 Sync Ideas to Notion",
        "desc": "Push top ideas → Contents DB",
    },
    "collect_analytics": {
        "label": "📊 Collect Analytics",
        "desc": "YT/Twitter/Medium/IG metrics",
    },
    "build_kb": {
        "label": "📚 Rebuild Knowledge Base",
        "desc": "Refresh master_brief.md from all sources",
    },
}


def render(REPO: Path):
    st.title("⚙️ Workflows")

    preselect = st.session_state.get("preselect_workflow")
    wf_keys = list(WORKFLOWS.keys())
    idx = wf_keys.index(preselect) if preselect in wf_keys else 0
    if preselect:
        st.session_state.pop("preselect_workflow", None)

    wf = st.selectbox(
        "Select workflow",
        wf_keys,
        index=idx,
        format_func=lambda k: WORKFLOWS[k]["label"],
    )
    st.caption(WORKFLOWS[wf]["desc"])
    st.divider()

    if wf == "daily_ideas":
        if st.button("Run daily_ideas.sh", type="primary"):
            with st.spinner("Running pipeline... (~5 min)"):
                res = run_cmd(["bash", "scripts/daily_ideas.sh"], cwd=REPO, timeout=900)
            show_run_result(res, "daily_ideas.sh")

    elif wf == "produce_blog":
        niche = st.selectbox("Niche", NICHES, format_func=lambda n: NICHE_LABELS[n])
        topic = st.text_input("Topic", value=st.session_state.get("picked_topic", ""))
        humanize = st.checkbox("Humanize pass (slower, better)", value=True)
        if st.button("Run", type="primary", disabled=not topic):
            args = ["--topic", topic, "--niche", niche]
            if humanize:
                args.append("--humanize")
            with st.spinner("Producing blog..."):
                res = run_cmd(py_cmd("scripts/produce_blog.py", *args), cwd=REPO, timeout=600)
            show_run_result(res, "produce_blog.py")

    elif wf == "ghostwrite":
        niche = st.selectbox("Niche", NICHES, format_func=lambda n: NICHE_LABELS[n])
        source = st.text_input("Source file path", placeholder="path/to/notes.txt")
        topic = st.text_input("Topic (optional)", value=st.session_state.get("picked_topic", ""))
        voice = st.selectbox("Voice", ["analytical", "conversational", "deletion", "decision"])
        desire = st.selectbox("Desire", ["clarity", "success", "status", "tribe", "fear", "enjoyment"])
        if st.button("Run", type="primary", disabled=not source):
            args = ["--source", source, "--niche", niche, "--voice", voice, "--desire", desire]
            if topic:
                args += ["--topic", topic]
            with st.spinner("Ghostwriting..."):
                res = run_cmd(py_cmd("scripts/ghostwrite.py", *args), cwd=REPO, timeout=600)
            show_run_result(res, "ghostwrite.py")

    elif wf == "fetch_images":
        niche = st.selectbox("Niche", NICHES, format_func=lambda n: NICHE_LABELS[n])
        input_path = st.text_input("Blog markdown path", placeholder="content/blogs/...")
        if st.button("Fetch", type="primary", disabled=not input_path):
            res = run_cmd(py_cmd("scripts/fetch_images.py", "--input", input_path, "--niche", niche), cwd=REPO, timeout=300)
            show_run_result(res, "fetch_images.py")

    elif wf == "fetch_videos":
        niche = st.selectbox("Niche", NICHES, format_func=lambda n: NICHE_LABELS[n])
        mode = st.radio("Source", ["YT script (uses [BROLL:] cues)", "Blog (Claude generates terms)"])
        path = st.text_input("Path", placeholder="content/scripts/..._yt.md" if "script" in mode else "content/blogs/...md")
        if st.button("Fetch", type="primary", disabled=not path):
            flag = "--script" if "script" in mode else "--input"
            res = run_cmd(py_cmd("scripts/fetch_videos.py", flag, path, "--niche", niche), cwd=REPO, timeout=600)
            show_run_result(res, "fetch_videos.py")

    elif wf == "repurpose_blog":
        path = st.text_input("Blog path", placeholder="content/blogs/...md")
        if st.button("Repurpose", type="primary", disabled=not path):
            res = run_cmd(py_cmd("scripts/repurpose_blog.py", "--input", path), cwd=REPO, timeout=600)
            show_run_result(res, "repurpose_blog.py")

    elif wf == "generate_design":
        path = st.text_input("Blog path", placeholder="content/blogs/...md")
        if st.button("Generate", type="primary", disabled=not path):
            res = run_cmd(py_cmd("scripts/generate_design_prompts.py", "--input", path), cwd=REPO, timeout=300)
            show_run_result(res, "generate_design_prompts.py")

    elif wf == "auto_edit":
        niche = st.selectbox("Niche", NICHES, format_func=lambda n: NICHE_LABELS[n])
        raw = st.text_input("Raw video path", placeholder="assets/raw/...mov")
        script = st.text_input("YT script path", placeholder="content/scripts/..._yt.md")
        slug = st.text_input("Output slug")
        skip_broll = st.checkbox("Skip broll", value=False)
        if st.button("Auto-edit", type="primary", disabled=not (raw and script and slug)):
            args = ["--raw", raw, "--script", script, "--niche", niche, "--slug", slug]
            if skip_broll:
                args.append("--skip-broll")
            with st.spinner("Editing... (~5 min)"):
                res = run_cmd(py_cmd("scripts/auto_edit.py", *args), cwd=REPO, timeout=1800)
            show_run_result(res, "auto_edit.py")

    elif wf == "clip_shorts":
        slug = st.text_input("Slug (must match edited mp4)", value=st.session_state.get("last_slug", ""))
        count = st.number_input("Number of shorts", 1, 8, 4)
        no_claude = st.checkbox("Skip claude (use even-spaced fallback)")
        if st.button("Generate", type="primary", disabled=not slug):
            args = ["--slug", slug, "--count", str(count)]
            if no_claude:
                args.append("--no-claude")
            with st.spinner("Cutting shorts..."):
                res = run_cmd(py_cmd("scripts/clip_shorts.py", *args), cwd=REPO, timeout=600)
            show_run_result(res, "clip_shorts.py")

    elif wf == "upload_youtube":
        video = st.text_input("Video path", placeholder="assets/video/edited/...mp4")
        slug = st.text_input("Slug")
        shorts = st.checkbox("Upload as Short")
        channel = st.selectbox("Channel", ["Breath of Data Science", "Breath of Life", "Breath of Poetry"]) if shorts else None
        if st.button("Upload", type="primary", disabled=not (video and slug)):
            args = ["--video", video, "--slug", slug]
            if shorts:
                args += ["--shorts", "--channel", channel]
            with st.spinner("Uploading..."):
                res = run_cmd(py_cmd("scripts/upload_youtube.py", *args), cwd=REPO, timeout=1800)
            show_run_result(res, "upload_youtube.py")

    elif wf == "publish_medium":
        path = st.text_input("Blog path", placeholder="content/blogs/...md")
        canonical = st.text_input("Canonical URL", placeholder="https://breathof...substack.com/...")
        if st.button("Publish", type="primary", disabled=not (path and canonical)):
            res = run_cmd(py_cmd("scripts/publish_medium.py", "--input", path, "--canonical-url", canonical), cwd=REPO, timeout=300)
            show_run_result(res, "publish_medium.py")

    elif wf == "load_posts":
        if st.button("Load to scheduling.db", type="primary"):
            res = run_cmd(py_cmd("scripts/load_posts.py"), cwd=REPO, timeout=300)
            show_run_result(res, "load_posts.py")

    elif wf == "sync_notion":
        dry = st.checkbox("Dry-run only", value=False)
        if st.button("Sync", type="primary"):
            args = ["--dry-run"] if dry else []
            res = run_cmd(py_cmd("scripts/sync_ideas_to_notion.py", *args), cwd=REPO, timeout=120)
            show_run_result(res, "sync_ideas_to_notion.py")

    elif wf == "collect_analytics":
        if st.button("Collect now", type="primary"):
            with st.spinner("Fetching analytics..."):
                res = run_cmd(py_cmd("scripts/collect_analytics.py"), cwd=REPO, timeout=600)
            show_run_result(res, "collect_analytics.py")

    elif wf == "build_kb":
        if st.button("Rebuild KB", type="primary"):
            with st.spinner("Rebuilding..."):
                res = run_cmd(py_cmd("scripts/build_knowledge_base.py"), cwd=REPO, timeout=900)
            show_run_result(res, "build_knowledge_base.py")
