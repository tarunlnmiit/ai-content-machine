#!/usr/bin/env bash
# HyperFrames Alpha Channel Spike
# Run from the v1/ directory: bash spike_hf_alpha.sh
# Paste ALL output back into the chat.
set -e

SPIKE_DIR="/tmp/hf_spike_$$"
mkdir -p "$SPIKE_DIR"
cd "$SPIKE_DIR"

echo "=== 1. ENVIRONMENT ==="
node --version 2>&1 || echo "node: not found"
npm --version  2>&1 || echo "npm: not found"
echo ""

echo "=== 2. HYPERFRAMES CLI DISCOVERY ==="
# Try the most likely package names
for PKG in hyperframes @heygen/hyperframes @hyperframes/cli; do
    printf "  npx %s --version ... " "$PKG"
    npx --yes --quiet "$PKG" --version 2>&1 | head -1 && continue || echo "not found"
done
echo ""

echo "=== 3. HYPERFRAMES SKILLS (Claude Code) ==="
for DIR in "$HOME/.claude/skills" "$HOME/.config/claude/skills"; do
    if [ -d "$DIR" ]; then
        echo "  Skills dir: $DIR"
        ls "$DIR/" | grep -i hyper || echo "    (no hyperframes skill found)"
    fi
done
echo ""

echo "=== 4. CHECK IF HYPERFRAMES ALREADY RUNNABLE ==="
if npx --quiet hyperframes --version 2>/dev/null; then
    echo "hyperframes IS available. Checking render options:"
    npx hyperframes render --help 2>&1 || npx hyperframes --help 2>&1 || true
    echo ""
    echo "=== 5. MINIMAL COMPOSITION RENDER TEST ==="
    cat > test_comp.html << 'COMP'
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { margin: 0; background: transparent; }
    #stage { position: relative; width: 1920px; height: 1080px; background: transparent; }
    .clip { position: absolute; top: 0; left: 0; width: 100%; height: 100%; }
    .label {
      position: absolute; top: 50%; left: 50%; transform: translate(-50%,-50%);
      font-family: sans-serif; font-size: 80px; color: white;
      text-shadow: 0 0 30px rgba(0,0,0,0.9);
    }
  </style>
</head>
<body>
  <div
    id="stage"
    data-composition-id="alpha-spike"
    data-width="1920"
    data-height="1080"
    data-fps="30"
    data-duration-secs="2"
  >
    <div
      class="clip"
      data-start="0"
      data-duration="2"
      data-track-index="0"
    >
      <div class="label">ALPHA TEST</div>
    </div>
  </div>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
  <script>
    window.__timelines = {};
    const tl = gsap.timeline({ paused: true });
    tl.from(".label", { opacity: 0, duration: 0.5, ease: "power2.out" });
    window.__timelines["alpha-spike"] = tl;
  </script>
</body>
</html>
COMP

    echo "  Rendering test_comp.html ..."
    npx hyperframes render test_comp.html --output alpha_test.mp4 2>&1 || \
    npx hyperframes render test_comp.html 2>&1 || \
    echo "  render command failed or has different syntax"

    echo ""
    echo "=== 6. FFPROBE OUTPUT FILES ==="
    for f in "$SPIKE_DIR"/*.mp4 "$SPIKE_DIR"/*.mov "$SPIKE_DIR"/*.webm; do
        [ -f "$f" ] || continue
        echo "  File: $f"
        ffprobe -v error -select_streams v:0 \
            -show_entries stream=codec_name,pix_fmt,codec_tag_string \
            -of default=noprint_wrappers=1 "$f" 2>&1
        echo ""
    done
else
    echo "  hyperframes CLI not yet available via npx."
    echo ""
    echo "=== 5. INSTALL HYPERFRAMES SKILL ==="
    echo "  To install: npx skills add heygen-com/hyperframes --all"
    echo "  (Requires Claude Code CLI to be logged in)"
    echo ""
    echo "  Attempting install now ..."
    npx skills add heygen-com/hyperframes --all 2>&1 | tail -20 || \
        echo "  Install failed — may need: claude login first"
fi

echo ""
echo "=== 7. FFMPEG / FFPROBE ==="
ffmpeg -version 2>&1 | head -1
ffprobe -version 2>&1 | head -1
echo ""

echo "=== 8. CLAUDE CLI ==="
which claude 2>/dev/null && claude --version 2>/dev/null || echo "claude: not in PATH"
echo ""

echo "=== SPIKE COMPLETE ==="
echo "Paste everything above into the chat."
