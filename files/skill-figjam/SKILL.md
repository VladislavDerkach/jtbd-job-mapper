---
name: jtbd-research-to-figjam
description: >
  Turns customer research (desk research, chat/interview corpora, transcripts, notes) into a full
  Jobs-to-be-Done package in the Advanced JTBD + Next Move Theory format (Ivan Zamesin):
  extracts jobs per user segment (B2C jobs, B2B business jobs and the decision-maker's personal job),
  describes each job as When / Want to / So that without inventing facts, exports the list to a Google
  Doc, draws job cards by segment in FigJam, builds a job graph (sequence and higher/lower-level
  links), rates which jobs a product covers, and draws a Next Move Theory segment map.
  Use this skill whenever the user asks to extract or describe jobs / JTBD / "customer jobs" from
  research, build a jobs list or job map, map user segments, draw jobs or segments in FigJam/Figma,
  or mentions Zamesin, Next Move Theory, Advanced JTBD, "segment map", "job graph" — even if
  they only ask for one of these steps.
---

# From research to jobs, a graph and a segment map (Advanced JTBD + Next Move Theory)

This skill walks a product manager from raw research to four artifacts:

1. **A job list** by segment in "When / Want to / So that" format (`work/jobs.json`, the source of truth).
2. **A Google Doc** (or Markdown/Word) with the full list.
3. **A FigJam board**: job cards in segment columns, with a copy next to it carrying the job graph.
4. **A segment map** per the Next Move Theory canon, next to it on the same board.

Honesty is the whole point of the result. The user bases product decisions on this list, so a made-up "fact" is worse than a blank. Every field is either taken from a source, labeled as the research author's hypothesis, labeled as an AI assumption, or left as a "—".

## Before you start

Read `references/job-format.md`: it has the job format and the labeling rules. Stages 1–3 can't be done right without it.

Collect from the user (one short question, if something's missing from their message):
- **sources**: files, links, pasted text;
- **the product**, if you'll need a fit rating (stage 7): its name and what it does today;
- **where to output to**: FigJam (needs the Figma MCP), a Google Doc (needs the Google Drive MCP), or files only.

Check the available tools. You need the Figma MCP (`use_figma`, `create_new_file`, `get_screenshot`, `whoami`) for stages 5–8, and the Google Drive MCP for stage 4. If something's missing, say so in one line and do the stages you can — hand over a `.md` instead of a Google Doc.

Working folder: `work/` in the current directory (on claude.ai: `/home/claude/work/`). Keep all intermediate data there so stages can be rerun.

## Pipeline

The stages run in order. Stop and show the result after stages 3, 5 and 6: the user almost always edits segments and links by hand, and the following stages need to build on their edits, not on your draft.

### Stage 1. Extract jobs from each source

Read `references/extraction-rules.md`.

- **Claude Code with subagents:** launch a `jtbd-extractor` subagent on each source in parallel (described in `agents/jtbd-extractor.md`; if the agent isn't installed, pass its text as a prompt to a general-purpose agent). Each one returns a JSON fragment following the schema in `references/jobs-schema.md`, with evidence quotes.
- **Without subagents:** process the sources yourself, one by one, by the same rules.

For each source, first decide its type: customer voice (corpus, interviews) or a market description (desk). The type decides the label in the `basis` field and whether the job can be treated as confirmed.

### Stage 2. Merge into one list and segment it

- Merge the fragments into `work/jobs.json` per the `references/jobs-schema.md` schema.
- Dedupe: one job seen in several sources becomes one record with several `evidence` entries.
- Sort jobs into segments. A segment is defined by who does the job and under what circumstances — not by demographics. If the same job shows up in several segments, record the main one in `segment` and the rest in `also_segments`.
- In B2B, look for the decision-maker's personal job next to every business job (`type: b2b-personal`, `pair_of`). If there's no data on the decision-maker, create the personal job anyway, but with an AI-assumption label or blanks.
- Assign every job a `job_type` (regular, orientation, Tax, Fake, emotional, viral) per section 4 of `references/extraction-rules.md`. Tax Job and Fake Job change product decisions, so name them explicitly.
- Run `python3 scripts/validate_jobs.py work/jobs.json`. Fix every error before the next stage.

### Stage 3. Review and fill gaps

- **Claude Code:** launch the `jtbd-auditor` subagent (`agents/jtbd-auditor.md`). It checks every field against the quotes and flags anything unsupported.
- Then, only if the user wants it, propose the missing pieces. Label every such piece `[AI-ASSUMPTION]` right in the field's text. The label must stay visible in the document and on the board (the board colors such lines orange automatically).
- **Checkpoint:** show the user a summary — segments, how many jobs in each, which jobs rest only on hypotheses, what's labeled `fake` and why, what's labeled `tax` (see extraction-rules). Ask what to fix.

### Stage 4. The job-list document

- `python3 scripts/render_markdown.py work/jobs.json work/jobs.md`
- If the Google Drive MCP is available: create a Google Doc from this Markdown (create a file, converting it to Google Docs). If Drive isn't available but the user asked for a file, hand over the `.md`; produce a Word file only on an explicit request.

### Stage 5. Job cards in FigJam

Read `references/figjam-rendering.md` in full: it has the call order, Figma's limits and the tested tricks. In short:

1. Load the Figma skills (`figma-use`, `figma-use-figjam`) via `get_figma_skill`, as the Figma MCP requires.
2. `whoami` → `create_new_file` (editorType `figjam`), or use the user's link.
3. `python3 scripts/build_figjam_code.py scaffold work/jobs.json work/code/` → run `work/code/01_scaffold.js` via `use_figma`. Save the response (board and column ids) into `work/figjam_state.json`, in the format described in the references.
4. `python3 scripts/build_figjam_code.py segments work/jobs.json work/code/ --state work/figjam_state.json` → run every `02_segments_*.js` in turn.
5. Check the result with `get_screenshot` (`enableBase64Response: true`) on one column. If something's off, fix it and rebuild that column, not the whole board.

**Checkpoint:** give the board's link and ask whether the jobs are laid out across segments the way they should be.

### Stage 6. The link graph

Read `references/job-graph.md`: the two kinds of links and the direction rules.

- Propose links in `jobs.json`'s `edges` only where a source or clear process logic backs them up; mark disputed ones `"basis": "AI-assumption"`.
- `build_figjam_code.py graph ...` → run `03_graph.js`. It copies the board to the right (Figma's Starter plan has one page, so the copy lands on the same page) and draws arrows.
- **Checkpoint:** ask the user to fix the graph by hand in FigJam and say when it's done.
- After the edit: `build_figjam_code.py read work/jobs.json work/code/ --root <graph_board from state>` → run `90_read_board.js`, save the response to `work/board_dump.json`, then `python3 scripts/sync_from_board.py work/jobs.json work/board_dump.json` and show the user what changed (new and removed segments, jobs, links). Update `jobs.json`.

### Stage 7. Product fit

You need a description of the product's current state. Get it from the user or from public sources (site, catalog), and say where it came from. Set `fit` for every job:
- `now`: the product covers the job already;
- `min`: it will, with minimal extra work (name it in `fit_note`);
- `none`: unrelated to the product.

Rate high-level jobs the product only covers through a lower-level job by the job itself, and mention the link in `fit_note`. Show the outcome as three groups and list the assumptions about the product worth checking.

### Stage 8. Next Move Theory segment map

Read `references/segment-map-nmt.md`. Fill in `goal`, `price`, `compete` on the segments, then `build_figjam_code.py segmap ...` → run `04_segment_map.js` and check it with a screenshot. Mark prices and goal statements the data doesn't have as hypotheses, right on the map.

## Common mistakes

- **Several verbs in one job.** "I want to hand over the boat and get the deposit back" isn't one job, it's a stack of two. Split by level and link with `part`; move constraints ("fast", "without a dispute") into the success criteria. The validator treats this as an error.
- **"I want there to be …".** The subject has drifted away from the person doing the job. Reword it: "I want to answer with a document, not words."
- **Fake Job by frequency.** A rare job doesn't mean fake. Fake is the absence of past investment (money, time, effort), and nothing else. Money that went to a competitor or substitute is proof the job is real.
- **Inventing things.** If the source has no trigger, write "—". Wanting it to "look nice" is not a reason to fill in a field.
- **Mixing up hypothesis labels.** "(hypothesis)" means the research author's conclusion, "[AI-ASSUMPTION]" means your own conclusion. Don't mix them.
- **Desk research numbers** usually have no primary source. Carry them over, but label "desk" in the basis.
- **Restructuring the board across several `use_figma` calls** breaks it: nodes moved between calls get lost. Create everything that belongs to one section in a single call, inside a section that already exists (details in `figjam-rendering.md`).
- **A board after a manual edit** counts as the truth. Never redraw over the user's edits; put new artifacts next to them.
