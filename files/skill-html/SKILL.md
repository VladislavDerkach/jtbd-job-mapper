---
name: jtbd-research-to-html
description: >
  Turns customer research (desk research, chat/interview corpora, transcripts, notes) into a full
  Jobs-to-be-Done package in the Advanced JTBD + Next Move Theory format (Ivan Zamesin), the same
  way jtbd-research-to-figjam does, but renders the job cards, the link graph and the Next Move
  Theory segment map into ONE self-contained HTML file instead of a FigJam board — no Figma MCP,
  no account, works offline, opens in any browser. Use this skill whenever the user asks for a jobs
  board, job map or segment map as a web page / HTML file / local file they can open in a browser,
  or explicitly doesn't want to use Figma/FigJam for it.
---

# From research to jobs, a graph and a segment map — in HTML (Advanced JTBD + Next Move Theory)

A sibling of `jtbd-research-to-figjam`. Exactly one difference: **the job graph and the segment map
render into a single HTML file that opens in a browser**, instead of a FigJam board. Stages 1–4 and 7
are identical word for word.

This skill walks a product manager from raw research to four artifacts:

1. **A job list** by segment in "When / Want to / So that" format (`work/jobs.json`, the source of truth).
2. **A Google Doc** (or Markdown/Word) with the full list.
3. **An HTML file**: job cards in segment columns, the link graph drawn over them, the segment map below. Opens in a browser, needs no internet connection.
4. **A segment map** per the Next Move Theory canon, in the same file.

Honesty is the whole point of the result. The user bases product decisions on this list, so a made-up "fact" is worse than a blank. Every field is either taken from a source, labeled as the research author's hypothesis, labeled as an AI assumption, or left as a "—".

## How this skill differs from the FigJam version

| | FigJam version | This version |
|---|---|---|
| Where it renders | a Figma board, needs the Figma MCP and a paid tier for large boards | a local HTML file, no dependencies |
| Graph and board copy | a separate board copy further right, arrows between cards | links are drawn over the columns, toggled with checkboxes |
| Editing by hand | the user drags cards around, then a `read` stage + `sync_from_board.py` reads the edits back | **there's no on-page editing** — you edit `jobs.json`, the file redraws in under a second |
| Segment map | a separate block on the board | a section at the bottom of the same page |
| Working together | several people on the board at once | the file is shared as a link or printed to PDF |

**The only thing lost next to the FigJam version is syncing edits back.** There, the user edited the board by hand and the skill read the edits back into `jobs.json`. Here there's exactly one source of truth — `jobs.json` — which is arguably a feature: the board and the file can never drift apart. If the user specifically needs manual card layout, that's a job for the FigJam version — say so plainly.

## Before you start

Read `references/job-format.md`: it has the job format and the labeling rules. Stages 1–3 can't be done right without it.

Collect from the user (one short question, if something's missing from their message):
- **sources**: files, links, pasted text;
- **the product**, if you'll need a fit rating (stage 7): its name and what it does today;
- **where to output to**: HTML (needs nothing extra), a Google Doc (needs the Google Drive MCP), or files only.

Check the available tools. HTML needs nothing but Python 3 and a browser. The Google Drive MCP is only needed for stage 4; without it, hand over a `.md` instead of a Google Doc.

Working folder: `work/` in the current directory (on claude.ai: `/home/claude/work/`). Keep all intermediate data there so stages can be rerun.

## Pipeline

The stages run in order. Stop and show the result after stages 3 and 5: the user almost always edits segments and links, and the following stages need to build on their edits, not on your draft.

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
- Then, only if the user wants it, propose the missing pieces. Label every such piece `[AI-ASSUMPTION]` right in the field's text. The label must stay visible in the document and on the page (the page colors such text orange automatically).
- **Checkpoint:** show the user a summary — segments, how many jobs in each, which jobs rest only on hypotheses, what's labeled `fake` and why, what's labeled `tax`. Ask what to fix.

### Stage 4. The job-list document

- `python3 scripts/render_markdown.py work/jobs.json work/jobs.md`
- If the Google Drive MCP is available: create a Google Doc from this Markdown. If Drive isn't available but the user asked for a file, hand over the `.md`; produce a Word file only on an explicit request.

### Stage 5. Cards, graph and segment map in HTML

Read `references/html-rendering.md`: what gets drawn, which flags exist, and what to check. One command does everything:

```
python3 scripts/render_html.py work/jobs.json work/jobs_graph.html --open
```

The script lays cards out in segment columns, draws the links from `edges` over the columns, adds a segment map at the bottom, and opens the file in a browser. Links are computed in the browser from the cards' real coordinates, so nothing needs manual positioning and nothing breaks when the window is resized.

Check the result by eye (or with a headless-Chrome screenshot, if you're the one looking): no cards cut off, only `[AI-ASSUMPTION]` text colored orange, lines never running through cards.

**Checkpoint:** hand over the file's path and ask whether the jobs are laid out across segments the way they should be, and whether the links are right.

### Stage 6. Editing the graph

The graph is edited **in `jobs.json`, not on the page**: add or remove entries in `edges` and redraw with the same command. Read `references/job-graph.md`: the two kinds of links and the direction rules.

- Only propose links where a source or clear process logic backs them up; mark disputed ones `"basis": "AI-assumption"` — the basis text shows up as a tooltip on the line.
- Redrawing takes under a second, so show the user intermediate versions freely.

### Stage 7. Product fit

You need a description of the product's current state. Get it from the user or from public sources (site, catalog), and say where it came from. Set `fit` for every job:
- `now`: the product covers the job already;
- `min`: it will, with minimal extra work (name it in `fit_note`);
- `none`: unrelated to the product.

Rate high-level jobs the product only covers through a lower-level job by the job itself, and mention the link in `fit_note`. `fit` shows up as a badge on the card and a circle on the segment map. Show the outcome as three groups and list the assumptions about the product worth checking.

### Stage 8. Next Move Theory segment map

Read `references/segment-map-nmt.md`. Fill in `goal`, `price`, `compete` on the segments — and redraw: the map is built from the same data, by the same command, no separate step. Mark prices and goal statements the data doesn't have as hypotheses right in `goal_basis`.

## Common mistakes

- **Several verbs in one job.** "I want to hand over the boat and get the deposit back" isn't one job, it's a stack of two. Split by level and link with `part`; move constraints ("fast", "without a dispute") into the success criteria. The validator treats this as an error.
- **"I want there to be …".** The subject has drifted away from the person doing the job. Reword it: "I want to answer with a document, not words."
- **Fake Job by frequency.** A rare job doesn't mean fake. Fake is the absence of past investment (money, time, effort), and nothing else. Money that went to a competitor or substitute is proof the job is real.
- **Inventing things.** If the source has no trigger, write "—". Wanting it to "look nice" is not a reason to fill in a field.
- **Mixing up hypothesis labels.** "(hypothesis)" means the research author's conclusion, "[AI-ASSUMPTION]" means your own conclusion. Don't mix them.
- **Desk research numbers** usually have no primary source. Carry them over, but label "desk" in the basis.
- **Editing the HTML by hand.** Never edit the generated file: the next redraw will overwrite it. Everything that needs to change goes into `jobs.json`.
- **Promising collaborative editing.** HTML cards can't be dragged around or commented on by two people at once. If the user specifically needs that, send them to the FigJam version honestly.
