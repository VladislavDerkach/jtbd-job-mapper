#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  JTBD Job Mapper — LOCAL installer
#  Run this AFTER `git clone`. Copies the 2 sub-agents and both skill
#  variants (jtbd-research-to-figjam, jtbd-research-to-html) from this
#  repo into ~/.claude/. Touches nothing else.
#
#  Author: Uladzislau Dziarkach (Vladislav Derkach)
#  https://www.linkedin.com/in/vladislavderkach/en/
# ─────────────────────────────────────────────────────────────
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
AGENTS_DIR="$CLAUDE_DIR/agents"
FIGJAM_DIR="$CLAUDE_DIR/skills/jtbd-research-to-figjam"
HTML_DIR="$CLAUDE_DIR/skills/jtbd-research-to-html"

echo ""
echo "  JTBD Job Mapper — local install"
echo "  source: $DIR"
echo "  → $AGENTS_DIR"
echo "  → $FIGJAM_DIR"
echo "  → $HTML_DIR"
echo ""

mkdir -p "$AGENTS_DIR" "$FIGJAM_DIR" "$HTML_DIR"

n=0
for f in "$DIR"/files/agents/*.md; do
  cp "$f" "$AGENTS_DIR/"
  echo "  ↓ agent    $(basename "$f")"
  n=$((n+1))
done

rm -rf "$FIGJAM_DIR" "$HTML_DIR"
cp -r "$DIR/files/skill-figjam" "$FIGJAM_DIR"
cp -r "$DIR/files/skill-html" "$HTML_DIR"
echo "  ↓ skill    jtbd-research-to-figjam/"
echo "  ↓ skill    jtbd-research-to-html/"

echo ""
echo "  ✓ Installed: $n agents + jtbd-research-to-figjam + jtbd-research-to-html"
echo ""
echo "  Next:"
echo "   1) Restart Claude Code (to pick up the new agents and skills)"
echo "   2) Check /agents — jtbd-extractor and jtbd-auditor should appear"
echo "   3) Give it your research and ask for a jobs board — it'll offer"
echo "      FigJam or a local HTML file"
echo ""
echo "  jtbd-research-to-figjam needs the Figma MCP for the board stages."
echo "  jtbd-research-to-html needs only Python 3 and a browser."
echo ""
