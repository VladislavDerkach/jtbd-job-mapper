#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  JTBD Job Mapper — installer for Claude Code
#  Installs 2 sub-agents + two skills (jtbd-research-to-figjam,
#  jtbd-research-to-html) into ~/.claude/. Touches nothing else.
#
#  Author: Uladzislau Dziarkach (Vladislav Derkach)
#  https://www.linkedin.com/in/vladislavderkach/en/
# ─────────────────────────────────────────────────────────────
set -euo pipefail

BASE="${JJM_BASE:-https://jtbd-job-mapper.dervlad.com}"
CLAUDE_DIR="$HOME/.claude"
AGENTS_DIR="$CLAUDE_DIR/agents"
FIGJAM_DIR="$CLAUDE_DIR/skills/jtbd-research-to-figjam"
HTML_DIR="$CLAUDE_DIR/skills/jtbd-research-to-html"

AGENTS=(jtbd-extractor jtbd-auditor)
FIGJAM_FILES=(
  "SKILL.md" "SKILL.md"
  "references/job-format.md" "references/job-format.md"
  "references/extraction-rules.md" "references/extraction-rules.md"
  "references/job-graph.md" "references/job-graph.md"
  "references/jobs-schema.md" "references/jobs-schema.md"
  "references/segment-map-nmt.md" "references/segment-map-nmt.md"
  "references/figjam-rendering.md" "references/figjam-rendering.md"
  "scripts/validate_jobs.py" "scripts/validate_jobs.py"
  "scripts/render_markdown.py" "scripts/render_markdown.py"
  "scripts/build_figjam_code.py" "scripts/build_figjam_code.py"
  "scripts/sync_from_board.py" "scripts/sync_from_board.py"
  "scripts/figjam/lib.js" "scripts/figjam/lib.js"
  "scripts/figjam/scaffold.js" "scripts/figjam/scaffold.js"
  "scripts/figjam/segments.js" "scripts/figjam/segments.js"
  "scripts/figjam/graph.js" "scripts/figjam/graph.js"
  "scripts/figjam/segmap.js" "scripts/figjam/segmap.js"
  "scripts/figjam/read.js" "scripts/figjam/read.js"
  "assets/jobs.example.json" "assets/jobs.example.json"
)
HTML_FILES=(
  "SKILL.md" "SKILL.md"
  "references/job-format.md" "references/job-format.md"
  "references/extraction-rules.md" "references/extraction-rules.md"
  "references/job-graph.md" "references/job-graph.md"
  "references/jobs-schema.md" "references/jobs-schema.md"
  "references/segment-map-nmt.md" "references/segment-map-nmt.md"
  "references/html-rendering.md" "references/html-rendering.md"
  "scripts/validate_jobs.py" "scripts/validate_jobs.py"
  "scripts/render_markdown.py" "scripts/render_markdown.py"
  "scripts/render_html.py" "scripts/render_html.py"
  "assets/jobs.example.json" "assets/jobs.example.json"
)

echo ""
echo "  JTBD Job Mapper — install"
echo "  → $AGENTS_DIR"
echo "  → $FIGJAM_DIR"
echo "  → $HTML_DIR"
echo ""

mkdir -p "$AGENTS_DIR" "$FIGJAM_DIR/references" "$FIGJAM_DIR/scripts/figjam" "$FIGJAM_DIR/assets"
mkdir -p "$HTML_DIR/references" "$HTML_DIR/scripts" "$HTML_DIR/assets"

for a in "${AGENTS[@]}"; do
  printf "  ↓ agent    %-42s" "$a.md"
  if curl -fsSL "$BASE/files/agents/$a.md" -o "$AGENTS_DIR/$a.md"; then echo "ok"; else echo "FAILED"; exit 1; fi
done

fetch_pairs() {
  local remote_base="$1" local_dir="$2"; shift 2
  local pairs=("$@")
  local i=0
  while [ $i -lt ${#pairs[@]} ]; do
    local rel="${pairs[$i]}"
    printf "  ↓ file     %-42s" "$rel"
    if curl -fsSL "$BASE/$remote_base/$rel" -o "$local_dir/$rel"; then echo "ok"; else echo "FAILED"; exit 1; fi
    i=$((i + 2))
  done
}

fetch_pairs "files/skill-figjam" "$FIGJAM_DIR" "${FIGJAM_FILES[@]}"
fetch_pairs "files/skill-html" "$HTML_DIR" "${HTML_FILES[@]}"

echo ""
echo "  ✓ Installed: jtbd-extractor, jtbd-auditor,"
echo "    /jtbd-research-to-figjam and /jtbd-research-to-html"
echo ""
echo "  Next:"
echo "   1) Restart Claude Code (to pick up the new agents and skills)"
echo "   2) Check /agents — jtbd-extractor and jtbd-auditor should appear"
echo "   3) Give it your research: \"turn these interview notes into a jobs"
echo "      board\" — it'll ask whether you want FigJam or an HTML file"
echo ""
echo "  jtbd-research-to-figjam needs the Figma MCP for the board stages."
echo "  jtbd-research-to-html needs only Python 3 and a browser."
echo ""
echo "  Author: Uladzislau Dziarkach (Vladislav Derkach)"
echo "  https://www.linkedin.com/in/vladislavderkach/en/"
echo ""
