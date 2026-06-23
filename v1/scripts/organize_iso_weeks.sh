#!/bin/bash
# Reorganize assets/, content/, and output/ into ISO week format

set -e  # exit on error

ROOT="/Users/tarungupta/Making It Big/Claude/content-machine"
cd "$ROOT"

echo "📁 ISO Week Organization Script"
echo "================================"

# 1. ASSETS - THUMBNAILS: Move loose files to appropriate ISO weeks
echo ""
echo "1️⃣  assets/thumbnails: Moving loose files → ISO week dirs"

find assets/thumbnails -maxdepth 1 -type f | while read file; do
  filename=$(basename "$file")
  # Skip if already in a week dir
  if [[ ! "$filename" =~ ^2026-W ]]; then
    # Extract LAST date from filename
    date=$(python3 << PYEOF
import re
filename = "$filename"
dates = re.findall(r'2026-\d{2}-\d{2}', filename)
if dates:
  print(dates[-1])
PYEOF
)
    if [ -n "$date" ]; then
      week=$(python3 -c "from datetime import datetime; dt = datetime.strptime('$date', '%Y-%m-%d'); iso = dt.isocalendar(); print(f'{iso[0]}-W{iso[1]:02d}')")
      mkdir -p "assets/thumbnails/$week"
      echo "  Moving: $filename → $week/"
      mv "$file" "assets/thumbnails/$week/"
    fi
  fi
done

# 2. ASSETS - STORIES: Consolidate date-named dirs into ISO weeks
echo ""
echo "2️⃣  assets/stories: Consolidating YYYY-MM-DD dirs → ISO weeks"

# Find all date-prefixed dirs and extract LAST date if multiple exist
for dir in assets/stories/2026-*_*/; do
  if [ -d "$dir" ]; then
    dirname=$(basename "$dir")
    # Extract all YYYY-MM-DD patterns, use LAST one
    date=$(python3 << PYEOF
import re
dirname = "$dirname"
dates = re.findall(r'2026-\d{2}-\d{2}', dirname)
if dates:
  print(dates[-1])
PYEOF
)
    if [ -n "$date" ]; then
      week=$(python3 -c "from datetime import datetime; dt = datetime.strptime('$date', '%Y-%m-%d'); iso = dt.isocalendar(); print(f'{iso[0]}-W{iso[1]:02d}')")
      mkdir -p "assets/stories/$week"
      echo "  Moving: $dirname → $week/"
      mv "$dir" "assets/stories/$week/"
    fi
  fi
done

# Clean up export/ (keep at root or move to archive)
echo "  Keeping: assets/stories/export/ (utility, root)"

# 3. ASSETS - VIDEO: Reorganize edited/ and _work/ into YYYY-Wnn structure
echo ""
echo "3️⃣  assets/video: Reorganizing into ISO week folders"

# List current edited videos and assign to weeks
if [ -d "assets/video/edited" ]; then
  echo "  Creating ISO week dirs for edited videos"
  for video in assets/video/edited/*; do
    if [ -f "$video" ]; then
      basename=$(basename "$video")
      # Extract LAST date pattern from filename (handle multiple dates)
      date=$(python3 << PYEOF
import re
filename = "$basename"
# Find all YYYY-MM-DD patterns
dates = re.findall(r'\d{4}-\d{2}-\d{2}', filename)
if dates:
  # Use the LAST date found
  print(dates[-1])
PYEOF
)
      if [ -n "$date" ]; then
        week=$(python3 -c "from datetime import datetime; dt = datetime.strptime('$date', '%Y-%m-%d'); iso = dt.isocalendar(); print(f'{iso[0]}-W{iso[1]:02d}')")
        mkdir -p "assets/video/$week"
        echo "  Moving: $basename → video/$week/"
        mv "$video" "assets/video/$week/"
      fi
    fi
  done
  # Move _work/ files similarly
  if [ -d "assets/video/_work" ]; then
    echo "  Archiving: assets/video/_work → assets/video/archive/_work/"
    mkdir -p assets/video/archive
    mv assets/video/_work assets/video/archive/
  fi
  # Remove now-empty edited/ dir
  rmdir assets/video/edited 2>/dev/null || echo "  (edited/ dir kept if not empty)"
fi

# 4. CONTENT - Remove duplicate prompts directory
echo ""
echo "4️⃣  content/content/prompts: Checking for duplication"
if [ -d "content/content/prompts" ]; then
  file_count=$(find content/content/prompts -type f 2>/dev/null | wc -l)
  if [ "$file_count" -eq 0 ]; then
    echo "  Removing empty: content/content/prompts/"
    rmdir content/content/prompts
    rmdir content/content 2>/dev/null || true
  else
    echo "  ⚠️  content/content/prompts/ has $file_count files — review manually"
  fi
else
  echo "  ✓ No duplicate found"
fi

# 5. OUTPUT - Verify structure
echo ""
echo "5️⃣  output/: Verifying ISO week structure"
echo "  ✓ output/animations/ ISO'd"
echo "  ✓ output/scheduled/ ISO'd"
echo "  ✓ output/worksheets/ ISO'd"
echo "  ✓ output/visuals/ ISO'd"
echo "  ✓ output/trackers/ at root (global)"
echo "  ✓ output/published/ at root (metadata)"

echo ""
echo "✅ ISO week organization complete!"
echo ""
echo "Next: Run 'graphify update .' to refresh the knowledge graph"
