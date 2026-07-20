#!/usr/bin/env python3
"""Generate the Breath Network design-system bundle (v1/design-system/).

Mirrors the repo's three token systems into self-contained HTML preview cards
for the claude.ai/design "Breath Network" project (synced via /design-sync):

  System A — data/brand/brand_kit.yaml        (carousel/social/deck/thumbnail)
  System B — data/kb/design/*_design.md       (video look bibles)
  System C — scripts/templates/worksheet_shell.html ("Breath Network" tokens)

The three palettes are INTENTIONALLY divergent — this script mirrors, never
reconciles. Every emitted file starts with `<!-- @dsCard group="..." -->` so
the Design System pane auto-indexes it. Output is a deterministic full rewrite
of v1/design-system/; re-sync only the files `git diff` reports as changed.

Usage:
    python3 v1/scripts/generate_design_system.py
"""

import ast
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.niche_config import load_brand_base  # noqa: E402

import yaml  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "design-system"
BRAND_KIT_FILE = REPO / "data" / "brand" / "brand_kit.yaml"
DESIGN_KB = REPO / "data" / "kb" / "design"
TEMPLATES = REPO / "scripts" / "templates"
THUMBNAIL_SCRIPT = REPO / "scripts" / "generate_thumbnail.py"

NICHES = ["data_science_tech", "life_self_dev", "poetry_quotes"]
NICHE_SHORT = {"data_science_tech": "DS", "life_self_dev": "Life", "poetry_quotes": "Poetry"}
BIBLE_FILE = {"data_science_tech": "ds_design.md", "life_self_dev": "life_design.md",
              "poetry_quotes": "poetry_design.md"}

# Pinned real artifacts to copy in as sample cards (relative to REPO).
# NEVER include LOCAL-ONLY gitignored artifacts (inbox-to-action*).
CAROUSEL_SAMPLES = {
    "data_science_tech": "assets/carousels/2026-07-06_data_science_tech_the-local-ai-agent-i-built-in-a-weekend-now-does-the-grunt-w_carousel.html",
    "life_self_dev": "assets/carousels/2026-07-06_life_self_dev_your-overloaded-self-improvement-schedule-is-slowly-making-y_carousel.html",
}
WORKSHEET_SAMPLES = {
    "data_science_tech": "content/worksheets/2026-W28/2026-07-10_data_science_tech_i-asked-5-senior-engineers-to-explain-a-vector-database-with_worksheet.html",
    "life_self_dev": "content/worksheets/2026-W28/2026-07-10_life_self_dev_high-emotional-intelligence-at-work-isnt-about-being-nice-it_worksheet.html",
}

GOOGLE_FONTS = ("https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700"
                "&family=Lora:ital@0;1&family=Nunito+Sans:wght@400;700"
                "&family=Playfair+Display:ital@0;1&family=DM+Sans:wght@400;700"
                "&family=Inter:wght@400;600;800&family=JetBrains+Mono"
                "&family=Instrument+Serif:ital@0;1&family=Montserrat:wght@400;600;800"
                "&family=Cormorant+Garamond:ital@0;1&display=swap")

DIVERGENCE_FOOTER = ("Systems A (brand kit) / B (video bibles) / C (worksheet shell) are "
                     "intentionally divergent palettes. Mirror only — do NOT reconcile. "
                     "Edit repo sources, never this project.")

HEX_RE = re.compile(r"#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b|rgba?\([^)]+\)")


# ── page shell ───────────────────────────────────────────────────────────────

def page(group: str, title: str, body: str, *, footer: str = "", bg: str = "#14121f",
         fg: str = "#EDE8DC") -> str:
    foot = f'<footer class="ds-foot">{footer}</footer>' if footer else ""
    return f"""<!-- @dsCard group="{group}" -->
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{GOOGLE_FONTS}" rel="stylesheet">
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:{bg};color:{fg};font-family:'Inter','Helvetica Neue',Arial,sans-serif;
       padding:36px;line-height:1.5}}
  h1{{font-size:26px;font-weight:800;letter-spacing:-0.02em;margin-bottom:4px}}
  h2{{font-size:15px;font-weight:600;text-transform:uppercase;letter-spacing:.12em;
      opacity:.55;margin:28px 0 12px}}
  .sub{{font-size:13px;opacity:.6;margin-bottom:8px}}
  .grid{{display:flex;flex-wrap:wrap;gap:14px}}
  .swatch{{width:150px;border-radius:10px;overflow:hidden;
           border:1px solid rgba(255,255,255,.12)}}
  .swatch .chip{{height:74px}}
  .swatch .meta{{padding:8px 10px;background:rgba(255,255,255,.05);font-size:11px}}
  .swatch .meta b{{display:block;font-size:12px;margin-bottom:2px}}
  .swatch .meta code{{font-family:'JetBrains Mono',monospace;opacity:.75}}
  table{{border-collapse:collapse;width:100%;font-size:13px;margin-bottom:8px}}
  th,td{{text-align:left;padding:7px 12px;border-bottom:1px solid rgba(255,255,255,.1)}}
  th{{font-size:11px;text-transform:uppercase;letter-spacing:.1em;opacity:.5}}
  td code,pre{{font-family:'JetBrains Mono',monospace;font-size:12px}}
  pre{{background:rgba(0,0,0,.35);border:1px solid rgba(255,255,255,.1);
      border-radius:8px;padding:14px;overflow:auto;white-space:pre-wrap}}
  .dot{{display:inline-block;width:13px;height:13px;border-radius:3px;
        vertical-align:-2px;margin-right:7px;border:1px solid rgba(255,255,255,.25)}}
  .tag{{display:inline-block;font-size:11px;padding:3px 10px;border-radius:20px;
       background:rgba(255,255,255,.09);margin:0 6px 6px 0}}
  .warn{{border:1px solid #E8745A;background:rgba(232,116,90,.08);border-radius:10px;
        padding:12px 16px;font-size:13px;margin:16px 0}}
  .specimen{{font-size:30px;margin:6px 0 14px}}
  .ds-foot{{margin-top:36px;padding-top:14px;border-top:1px solid rgba(255,255,255,.12);
           font-size:11px;opacity:.55}}
</style>
</head>
<body>
{body}
{foot}
</body>
</html>
"""


def swatch(name: str, hexval: str, note: str = "") -> str:
    note_html = f"<span>{note}</span>" if note else ""
    return (f'<div class="swatch"><div class="chip" style="background:{hexval}"></div>'
            f'<div class="meta"><b>{name}</b><code>{hexval}</code> {note_html}</div></div>')


def write(rel: str, content: str) -> None:
    dest = OUT / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content)
    print(f"  wrote {rel}")


# ── System A: brand kit foundations ─────────────────────────────────────────

def emit_brand_core(kit: dict) -> None:
    colors, cp = kit["colors"], kit["carousel_palette"]
    body = (f"<h1>Brand Core — Global Palette</h1>"
            f'<p class="sub">Source: v1/data/brand/brand_kit.yaml (System A). '
            f'Creator: {kit["creator"]} · {kit["handle"]}</p>'
            "<h2>Global colors</h2><div class='grid'>"
            + swatch("Background", colors["background"], "dark slide bg")
            + swatch("Cream", colors["cream"], "light slide bg")
            + swatch("Slate blue", colors["slate_blue"], "DS/Tech primary")
            + swatch("Golden", colors["golden"], "Poetry primary")
            + swatch("Coral", colors["coral"], "Life primary, universal CTA")
            + "</div><h2>Derived 6-token carousel palette</h2><div class='grid'>"
            + "".join(swatch(k, v) for k, v in cp.items())
            + "</div>")
    write("foundations/brand-core/index.html",
          page("Foundations · Brand Core", "Brand Core — Global", body,
               footer=DIVERGENCE_FOOTER))

    for niche in NICHES:
        b = load_brand_base(niche)
        short = NICHE_SHORT[niche]
        body = (f"<h1>{b['brand_name']}</h1>"
                f'<p class="sub">{b["label"]} · {b["handle"]} · System A per-niche tokens</p>'
                "<h2>Palette</h2><div class='grid'>"
                + swatch("Primary", b["primary"]) + swatch("Light", b["light"])
                + swatch("Dark", b["dark_color"]) + swatch("Light bg", b["light_bg"])
                + swatch("Dark bg", b["dark_bg"])
                + "</div><h2>Typography</h2>"
                f"<table><tr><th>Role</th><th>Font</th></tr>"
                f"<tr><td>Heading</td><td>{b['font_heading']}</td></tr>"
                f"<tr><td>Body</td><td>{b['font_body']}</td></tr>"
                f"<tr><td>Style</td><td>{b['font_style']}</td></tr></table>"
                f"<div class='specimen' style=\"font-family:'{b['font_heading']}',serif;"
                f"color:{b['light']}\">The quick brown fox — {b['font_heading']}</div>"
                f"<div class='specimen' style=\"font-family:'{b['font_body']}',sans-serif;"
                f"font-size:18px\">Body specimen in {b['font_body']} — jumps over the lazy dog.</div>"
                f"<h2>Tone</h2><p>{b['tone']}</p>"
                f"<h2>Generation</h2><p class='sub'>claude_temperature {b['temperature']}</p>")
        write(f"foundations/brand-core/{short.lower()}.html",
              page("Foundations · Brand Core", f"Brand Core — {short}", body,
                   footer=DIVERGENCE_FOOTER, bg=b["dark_bg"]))


# ── System B: video look bibles ──────────────────────────────────────────────

def md_sections(text: str) -> dict:
    """Split look-bible markdown into {header: body} by '## ' headings."""
    parts = re.split(r"^## +(.+?)\s*$", text, flags=re.M)
    return {parts[i].strip(): parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def md_table_html(section: str, colorize: bool = False) -> str:
    """Render markdown pipe-tables in a section to HTML; optionally add color dots."""
    rows = [ln for ln in section.splitlines() if ln.strip().startswith("|")]
    if not rows:
        return ""
    out, header_done = ["<table>"], False
    for ln in rows:
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if set("".join(cells)) <= {"-", ":", " "}:
            continue
        tag = "td" if header_done else "th"
        rendered = []
        for c in cells:
            c = c.replace("`", "")
            m = HEX_RE.search(c) if colorize else None
            dot = f'<span class="dot" style="background:{m.group(0)}"></span>' if m else ""
            rendered.append(f"<{tag}>{dot}{c}</{tag}>")
        out.append("<tr>" + "".join(rendered) + "</tr>")
        header_done = True
    out.append("</table>")
    return "".join(out)


def emit_video_bibles() -> None:
    for niche in NICHES:
        src = DESIGN_KB / BIBLE_FILE[niche]
        short = NICHE_SHORT[niche]
        secs = md_sections(src.read_text())
        palette = secs.get("PALETTE", "")
        if not HEX_RE.search(palette):
            sys.exit(f"FATAL: no hex tokens parsed from PALETTE in {src.name} — "
                     "look-bible format changed; update generate_design_system.py parser.")
        banned_key = next((k for k in secs if k.startswith("BANNED")), None)
        durations = "\n".join(ln for ln in secs.get("MOTION LANGUAGE", "").splitlines()
                              if ln.strip().startswith("-"))
        grade = secs.get("COLOR GRADE", "").strip()
        body = (f"<h1>Video Look Bible — {short}</h1>"
                f'<p class="sub">Source: v1/data/kb/design/{src.name} (System B) — '
                f"HyperFrames/Remotion beat builders read this verbatim.</p>"
                "<h2>Palette</h2>" + md_table_html(palette, colorize=True)
                + "<h2>Typography</h2>" + md_table_html(secs.get("TYPOGRAPHY", ""))
                + "<h2>Motion language</h2>" + md_table_html(secs.get("MOTION LANGUAGE", ""))
                + f"<pre>{durations}</pre>"
                + "<h2>Color grade</h2>" + f"<pre>{grade}</pre>"
                + "<h2>Banned</h2>"
                + f"<pre>{secs.get(banned_key, '').strip()}</pre>")
        write(f"foundations/video/{short.lower()}.html",
              page("Foundations · Video Look Bibles", f"Video Bible — {short}", body,
                   footer=DIVERGENCE_FOOTER, bg="#0a0e1a", fg="#f0f4ff"))

    cat = (DESIGN_KB / "layout_catalogue.md").read_text()
    csecs = md_sections(cat)
    body = ("<h1>Layout Catalogue (v4)</h1>"
            '<p class="sub">Source: v1/data/kb/design/layout_catalogue.md — shared by all '
            "three niches. 52 block types × 9 position zones.</p>"
            "<h2>Position zones</h2>" + md_table_html(csecs.get("POSITION ZONES", ""))
            + "<h2>Block catalogue</h2>" + md_table_html(csecs.get("BLOCK CATALOGUE", ""))
            + "<h2>Selection rules</h2>"
            + f"<pre>{csecs.get('SELECTION RULES', '').strip()}</pre>")
    write("foundations/video/layout-catalogue.html",
          page("Foundations · Video Look Bibles", "Layout Catalogue", body,
               footer=DIVERGENCE_FOOTER, bg="#0a0e1a", fg="#f0f4ff"))


# ── System C: worksheet shell ────────────────────────────────────────────────

def emit_worksheet_foundation(shell: str) -> None:
    root = re.search(r":root\s*\{(.*?)\}", shell, re.S)
    tokens = dict(re.findall(r"(--[\w-]+):\s*([^;]+);", root.group(1))) if root else {}
    color_tokens = {k: v.strip() for k, v in tokens.items() if v.strip().startswith("#")}
    font_tokens = {k: v.strip() for k, v in tokens.items() if "font" in k}
    body = ("<h1>Worksheet — “Breath Network” Tokens</h1>"
            '<p class="sub">Source: v1/scripts/templates/worksheet_shell.html :root '
            "(System C). A4-landscape PDF worksheets, DS & Life niches only.</p>"
            "<h2>Colors</h2><div class='grid'>"
            + "".join(swatch(k, v) for k, v in color_tokens.items())
            + "</div><h2>Fonts</h2><table><tr><th>Token</th><th>Stack</th></tr>"
            + "".join(f"<tr><td><code>{k}</code></td><td>{v}</td></tr>"
                      for k, v in font_tokens.items())
            + "</table>")
    write("foundations/worksheet/index.html",
          page("Foundations · Worksheet", "Worksheet Tokens", body,
               footer=DIVERGENCE_FOOTER, bg="#1C1C2E", fg="#E8E0D5"))


def emit_worksheet_shell_preview(shell: str) -> None:
    section = (TEMPLATES / "worksheet_section.html").read_text()
    filled_section = (section.replace("__NUM__", "1")
                      .replace("__TITLE__", "Sample section title")
                      .replace("__NOTES_LABEL__", "Notes")
                      .replace("__CONTENT_HTML__",
                               '<div class="prompts"><div class="prompt">Sample prompt line '
                               "with <strong>bold</strong> and <em>editorial em</em>.</div>"
                               '<div class="prompt">Second prompt with <code>inline code</code>.'
                               "</div></div>"))
    html = (shell.replace("__DOC_TITLE__", "Breath Network — Worksheet Shell Preview")
            .replace("__EYEBROW__", "Breath Network · Worksheet")
            .replace("__TITLE_HTML__", "Shell preview with <em>editorial emphasis</em>")
            .replace("__TAGLINE__", "Placeholder content rendering the shell + one section "
                                    "template exactly as the generator fills them.")
            .replace("__FIELD3_LABEL__", "Focus")
            .replace("__SECTIONS__", filled_section * 3))
    html = html.replace("</head>", "<style>html{zoom:.6}</style>\n</head>", 1)
    write("components/worksheet/shell.html",
          '<!-- @dsCard group="Worksheet" -->\n' + html)


# ── copied real artifacts ────────────────────────────────────────────────────

def emit_copies() -> None:
    for niche, rel in CAROUSEL_SAMPLES.items():
        src = REPO / rel
        html = src.read_text().replace("</head>", "<style>html{zoom:.45}</style>\n</head>", 1)
        short = NICHE_SHORT[niche]
        write(f"components/carousel/{short.lower()}/sample.html",
              f'<!-- @dsCard group="Carousel · {short}" -->\n' + html)
    for niche, rel in WORKSHEET_SAMPLES.items():
        src = REPO / rel
        html = src.read_text().replace("</head>", "<style>html{zoom:.6}</style>\n</head>", 1)
        write(f"components/worksheet/sample-{NICHE_SHORT[niche].lower()}.html",
              '<!-- @dsCard group="Worksheet" -->\n' + html)


# ── authored component previews ──────────────────────────────────────────────

def carousel_archetypes(niche: str) -> str:
    b = load_brand_base(niche)
    grad = (f"linear-gradient(165deg, {b['dark_color']} 0%, {b['primary']} 50%, "
            f"{b['light']} 100%)")
    slide_css = f"""
  .slides{{display:flex;gap:20px;flex-wrap:wrap}}
  .slide{{width:324px;height:405px;border-radius:12px;overflow:hidden;position:relative;
         display:flex;flex-direction:column;padding:26px 24px;
         font-family:'{b['font_body']}','{b['font_heading']}',sans-serif}}
  .slide .label{{position:absolute;top:8px;right:12px;font-size:10px;opacity:.55;
                text-transform:uppercase;letter-spacing:.1em}}
  .slide.light{{background:{b['light_bg']};color:{b['dark_bg']}}}
  .slide.dark{{background:{b['dark_bg']};color:{b['light_bg']}}}
  .slide.grad{{background:{grad};color:#fff}}
  .hook{{font-family:'{b['font_heading']}',sans-serif;font-weight:700;font-size:27px;
        line-height:1.15;letter-spacing:-0.02em;margin-top:auto}}
  .kicker{{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
          color:{b['primary']}}}
  .slide.dark .kicker,.slide.grad .kicker{{color:{b['light']}}}
  .body-txt{{font-size:15px;line-height:1.5;margin-top:12px}}
  .cta{{margin-top:auto;align-self:flex-start;background:#fff;color:{b['dark_color']};
       font-weight:700;font-size:14px;padding:10px 20px;border-radius:24px}}
  .bar{{height:3px;border-radius:2px;background:{b['primary']};width:38%;margin-bottom:14px}}
"""
    body = (f"<h1>Carousel Slide Archetypes — {NICHE_SHORT[niche]}</h1>"
            f'<p class="sub">{b["brand_name"]} · tokens from brand_kit.yaml, structure from '
            f"generate_carousel.py (.ig-frame / .slide, 1080×1350 exported via Playwright).</p>"
            f"<style>{slide_css}</style>"
            '<div class="slides">'
            '<div class="slide light"><span class="label">Hook</span><div class="bar"></div>'
            '<span class="kicker">Hook slide</span>'
            '<div class="hook">Bold claim that stops the scroll goes here.</div></div>'
            '<div class="slide dark"><span class="label">Body</span>'
            '<span class="kicker">Body slide</span>'
            '<div class="body-txt">One idea per slide. Short lines. Progress bar up top, '
            "badge + follow chip in the real export. Dark slides alternate with light for "
            "rhythm.</div></div>"
            '<div class="slide grad"><span class="label">CTA</span>'
            '<span class="kicker">CTA slide</span>'
            '<div class="hook">Save this. Follow for the next one.</div>'
            f'<div class="cta">Follow {b["handle"]}</div></div>'
            "</div>")
    return page(f"Carousel · {NICHE_SHORT[niche]}",
                f"Carousel Archetypes — {NICHE_SHORT[niche]}", body, bg=b["dark_bg"])


def social_preview(niche: str) -> str:
    b = load_brand_base(niche)
    body = (f"<h1>Social Image — {NICHE_SHORT[niche]}</h1>"
            '<p class="sub">Template preview · generate_social_images.py (System A tokens). '
            "Real output: 1080×1080 quote/stat card.</p>"
            f"<div style=\"width:420px;height:420px;border-radius:14px;background:{b['dark_bg']};"
            f"display:flex;flex-direction:column;justify-content:center;padding:40px;\">"
            f"<div style=\"width:44px;height:4px;background:{b['primary']};margin-bottom:22px\"></div>"
            f"<div style=\"font-family:'{b['font_heading']}',serif;font-size:26px;font-weight:700;"
            f"line-height:1.3;color:{b['light_bg']}\">A quotable line from the blog goes here, "
            "set large and unhurried.</div>"
            f"<div style=\"margin-top:26px;font-size:13px;color:{b['light']}\">"
            f"{b['brand_name']} · {b['handle']}</div></div>")
    return page(f"Social Image · {NICHE_SHORT[niche]}",
                f"Social Image — {NICHE_SHORT[niche]}", body, bg="#14121f")


def deck_preview() -> str:
    b = load_brand_base("data_science_tech")
    body = ("<h1>Slide Deck</h1>"
            '<p class="sub">Template preview · generate_slide_deck.py — 7-slide HTML deck, '
            "System A tokens (DS shown; other niches swap primary/fonts).</p>"
            f"<div style=\"width:560px;height:315px;border-radius:12px;background:{b['dark_bg']};"
            "padding:34px;display:flex;flex-direction:column\">"
            f"<div style=\"font-size:11px;letter-spacing:.1em;text-transform:uppercase;"
            f"color:{b['primary']};font-weight:700\">Slide 01 · Title</div>"
            f"<div style=\"font-family:'{b['font_heading']}',sans-serif;font-size:30px;"
            f"font-weight:700;color:{b['light_bg']};margin-top:auto;line-height:1.2\">"
            "Deck title slide with brand tokens</div>"
            f"<div style=\"height:4px;width:70px;background:{b['primary']};margin-top:16px\"></div>"
            "</div>")
    return page("Slide Deck", "Slide Deck", body, bg="#14121f")


def load_canva_cfg() -> dict:
    """Extract _CANVA_NICHE_CFG dict literal from generate_thumbnail.py (no import —
    that module pulls heavy deps). Mirror it honestly, drift included."""
    tree = ast.parse(THUMBNAIL_SCRIPT.read_text())
    for node in ast.walk(tree):
        if (isinstance(node, ast.AnnAssign) or isinstance(node, ast.Assign)):
            targets = [node.target] if isinstance(node, ast.AnnAssign) else node.targets
            for t in targets:
                if isinstance(t, ast.Name) and t.id == "_CANVA_NICHE_CFG":
                    return ast.literal_eval(node.value)
    sys.exit("FATAL: _CANVA_NICHE_CFG not found in generate_thumbnail.py — parser drift.")


def thumbnail_preview(niche: str, cfg: dict) -> str:
    c = cfg[niche]
    body = (f"<h1>Thumbnail — {NICHE_SHORT[niche]}</h1>"
            f'<p class="sub">Canva AI pipeline · generate_thumbnail.py::_CANVA_NICHE_CFG '
            f'({c["brand"]} · {c["channel"]}).</p>'
            '<div class="warn">Known drift — intentional mirror: this config is a hand-copied '
            "mirror of brand_kit.yaml inside generate_thumbnail.py and adds an off-palette "
            f'pop color <code>{c["pop"]}</code> not present in the brand kit. Do not "fix" '
            "here; the source of truth for this card IS the drifted dict.</div>"
            "<h2>Tokens</h2><div class='grid'>"
            + swatch("Background", "#1E1B2E", "locked navy")
            + swatch("Accent", c["accent"]) + swatch("Pop", c["pop"], "off-palette")
            + "</div>"
            f"<h2>Style</h2><p>{c['style']}</p><p class='sub'>Font: {c['font']} · "
            "left/right split: face one side, giant hook text other side · hook ≥35% canvas "
            "width · readable at 120px.</p>"
            "<div style=\"margin-top:14px;width:480px;height:270px;border-radius:10px;"
            "background:#1E1B2E;display:flex;align-items:center;overflow:hidden\">"
            "<div style=\"width:42%;height:100%;background:rgba(255,255,255,.08);display:flex;"
            "align-items:center;justify-content:center;font-size:12px;opacity:.5\">face zone</div>"
            f"<div style=\"flex:1;padding:20px;font-family:'{c['font'].split(' +')[0]}',sans-serif;"
            f"font-weight:800;font-size:34px;line-height:1.1;color:{c['accent']}\">HOOK TEXT "
            f"<span style=\"color:{c['pop']}\">POPS</span></div></div>")
    return page(f"Thumbnail · {NICHE_SHORT[niche]}", f"Thumbnail — {NICHE_SHORT[niche]}", body)


# ── docs ─────────────────────────────────────────────────────────────────────

def emit_docs() -> None:
    body = ("<h1>Breath Network — Design System Mirror</h1>"
            '<p class="sub">Generated by v1/scripts/generate_design_system.py from the '
            "content-machine repo. This project is a READ-ONLY MIRROR.</p>"
            '<div class="warn"><b>The rule:</b> the repo holds three intentionally divergent '
            "token systems — A: brand_kit.yaml (carousel/social/deck/thumbnail), B: video "
            "look bibles (data/kb/design/*.md), C: worksheet shell (Breath Network tokens). "
            "They are visually adjacent but numerically unrelated ON PURPOSE. Do NOT "
            "reconcile them, and never edit files in this project directly — edit the repo "
            "sources and re-run the generator.</div>"
            "<h2>Systems</h2><table>"
            "<tr><th>System</th><th>Source</th><th>Consumers</th></tr>"
            "<tr><td>A · Brand kit</td><td><code>v1/data/brand/brand_kit.yaml</code></td>"
            "<td>carousel, social images, slide deck, script images, thumbnail</td></tr>"
            "<tr><td>B · Video bibles</td><td><code>v1/data/kb/design/*_design.md</code></td>"
            "<td>HyperFrames / Remotion beat builders</td></tr>"
            "<tr><td>C · Worksheet</td><td><code>v1/scripts/templates/worksheet_shell.html"
            "</code></td><td>generate_worksheet_html.py → A4 PDF</td></tr></table>"
            "<h2>Known drift (documented, intentional)</h2>"
            "<p><code>generate_thumbnail.py::_CANVA_NICHE_CFG</code> hand-mirrors the brand "
            "kit and adds off-palette pop colors — see the Thumbnail cards.</p>"
            "<h2>Gaps</h2><p>Poetry niche has no recent real carousel artifact — archetype "
            "card only. Worksheets are DS & Life only by design.</p>")
    write("docs/index.html", page("Docs", "Breath Network — Overview", body))

    body = ("<h1>Re-sync Procedure</h1>"
            '<p class="sub">Governance loop for keeping this mirror truthful.</p>'
            "<h2>When a source changes → affected cards</h2><table>"
            "<tr><th>Source file</th><th>Cards to re-sync</th></tr>"
            "<tr><td><code>brand_kit.yaml</code></td><td>Brand Core (4), Carousel archetypes, "
            "Social (3), Deck</td></tr>"
            "<tr><td><code>*_design.md</code> / <code>layout_catalogue.md</code></td>"
            "<td>Video Look Bibles (4)</td></tr>"
            "<tr><td><code>worksheet_shell.html</code> / <code>worksheet_section.html</code>"
            "</td><td>Worksheet tokens + shell preview</td></tr>"
            "<tr><td><code>generate_thumbnail.py</code> (_CANVA_NICHE_CFG)</td>"
            "<td>Thumbnail (3)</td></tr>"
            "<tr><td>New pinned sample artifacts</td><td>Carousel/Worksheet sample cards "
            "(update pins at top of generator)</td></tr></table>"
            "<h2>Steps</h2><pre>1. python3 v1/scripts/generate_design_system.py\n"
            "2. git diff --name-only v1/design-system/   # changed files only\n"
            "3. /design-sync — finalize_plan + write_files for changed paths\n"
            "   (deletes for removed files; never wholesale replace)</pre>"
            "<p class='sub'>Full guide: v1/docs/guides/design-system-sync.md</p>")
    write("docs/resync.html", page("Docs", "Re-sync Procedure", body))


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    kit = yaml.safe_load(BRAND_KIT_FILE.read_text())
    shell = (TEMPLATES / "worksheet_shell.html").read_text()

    if OUT.exists():
        shutil.rmtree(OUT)
    print(f"Generating design-system bundle → {OUT.relative_to(REPO)}/")

    emit_docs()
    emit_brand_core(kit)
    emit_video_bibles()
    emit_worksheet_foundation(shell)
    emit_worksheet_shell_preview(shell)
    emit_copies()

    for niche in NICHES:
        short = NICHE_SHORT[niche].lower()
        write(f"components/carousel/{short}/archetypes.html", carousel_archetypes(niche))
        write(f"components/social/{short}.html", social_preview(niche))
    write("components/deck/index.html", deck_preview())
    canva = load_canva_cfg()
    for niche in NICHES:
        write(f"components/thumbnail/{NICHE_SHORT[niche].lower()}.html",
              thumbnail_preview(niche, canva))

    files = sorted(OUT.rglob("*.html"))
    missing = [f for f in files if "@dsCard" not in f.read_text()[:200]]
    if missing:
        sys.exit(f"FATAL: files missing @dsCard marker: {missing}")
    print(f"Done — {len(files)} cards, all @dsCard-marked.")


if __name__ == "__main__":
    main()
