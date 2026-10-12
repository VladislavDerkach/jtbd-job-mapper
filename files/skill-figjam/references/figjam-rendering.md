# Rendering to FigJam via the Figma MCP

## Setup (once per session)

1. Load the Figma skills: `get_figma_skill` for `skill://figma/figma-use/SKILL.md` and `skill://figma/figma-use-figjam/SKILL.md` (with the Figma plugin in Claude Code these are the `/figma-use` and `/figma-use-figjam` skills). Pass `skillNames: "figma-use,figma-use-figjam"` to every `use_figma` call (prefixed `resource:` on claude.ai).
2. You need a file: the user's link (the fileKey from `figma.com/board/<fileKey>/…`) or a new one: `whoami` → `planKey`, then `create_new_file` with `editorType: "figjam"`.

## Call order

```
python3 scripts/build_figjam_code.py scaffold work/jobs.json work/code/ --check
  use_figma(code = contents of work/code/01_scaffold.js)
  → response {board, segments} + file_key  →  work/figjam_state.json
python3 scripts/build_figjam_code.py segments work/jobs.json work/code/ --state work/figjam_state.json --check
  use_figma(02_segments_01.js), use_figma(02_segments_02.js), …
get_screenshot(nodeId = one column, enableBase64Response = true)   # check
python3 scripts/build_figjam_code.py graph   … --state …  → use_figma(03_graph.js)   → save graph_board into state
python3 scripts/build_figjam_code.py read    … --root <graph_board> → use_figma(90_read_board.js) → work/board_dump.json
python3 scripts/build_figjam_code.py segmap  …                       → use_figma(04_segment_map.js)
```

Pass the `.js` file's contents into `code` verbatim. Don't rewrite the script by hand: it's tested and lays out nodes respecting the limits below. To rebuild a single column, run `segments --only <segment_id>`: the script clears only that column.

## Figma limits that already cost time

- **MCP call limit on the Starter tier.** The free tier hits the `use_figma` call limit fast. Save calls: don't make trial calls, check syntax locally (`--check`), screenshot one column instead of after every step. If the limit is used up, stop, tell the user, and leave the generated `.js` files: they can run them later or in another session.
- **One page on Starter.** `figma.createPage()` fails. The graph board copy and the segment map go on the same page, further right (the scripts find free space on their own).
- **Moving nodes between calls breaks them.** A node created in one `use_figma` call and `appendChild`-ed in another can get lost. That's why scaffold creates empty section columns, and each column is filled in full in a single call, inside a section that already exists.
- **Code size** is capped at 50,000 characters per call; the builder cuts batches at 45,000.
- **Wrapping text** needs `textAutoResize = 'HEIGHT'` and a fixed width; the Inter Regular/Medium/Bold fonts are preloaded.
- **Lists** in FigJam text are made with `setRangeListOptions` and `setRangeIndentation`; every list line needs its type set explicitly.
- **Screenshots**: request with `enableBase64Response: true` — an image link isn't reachable from the sandbox.

## Style (as in Zamesin's own examples)

- Job card: a white section; on the left a blue block with the number and title (for B2B, prefixed "Business job:" or "Decision-maker's personal job:"), a green "Segment" block, a grey "Basis" block; a copy from another segment gets an extra purple "Alternative User Segment" block. On the right, text: bold "When:", "Want to …", "So that", with bulleted sub-points.
- Segment column: a colored section, a brown header "Segment N. Name", an optional paragraph below it.
- Text containing `[AI-ASSUMPTION]` is colored orange.
- Graph: a solid orange arrow (`seq`), a dashed teal arrow (`part`), a grey dotted line with no arrows (copies).
- Segment map: tan "Competing" cards, white-with-border "Not competing" cards, three-state circles.

## If something went wrong

- A `segment section not found` response: the user deleted or recreated a column. Re-running scaffold for only the new segments won't work; it's simpler to create a new board with scaffold and carry the state over.
- Cards are clipped or overlapping: re-run that column with `--only`.
- The user has already edited the board by hand: never redraw over it — only `read`, then `sync_from_board.py`.
