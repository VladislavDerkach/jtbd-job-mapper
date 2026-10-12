# Rendering to HTML

A replacement for the FigJam version's `figjam-rendering.md`. No tooling needed beyond Python 3 and a browser.

## One command

```
python3 scripts/render_html.py work/jobs.json work/jobs_graph.html --open
```

| Flag | What it does |
|---|---|
| `--open` | opens the file in a browser (`open` on macOS, `startfile` on Windows, `webbrowser` on Linux) |
| `--no-graph` | cards only: no lines, no control bar. For printing, or when `edges` isn't filled in yet |
| `--no-segmap` | no segment map at the bottom |
| `--only SEG_ID ...` | only the given segments (their `id`); cross-segment links aren't drawn then |

Redrawing takes under a second, so show the user intermediate versions as often as you like. Re-running overwrites the same file — refreshing the browser tab is enough.

## What gets drawn

**Job card.** A blue plate with the number and title (for B2B, prefixed "Business job:" or "Decision-maker's personal job:"), a job-type plate, a green "Segment" plate, a grey "Basis" plate, and a purple "Alternative User Segment" plate for a copy from another segment. Below, the text: "When:" with four points, "Want to …" with success criteria, "So that …" with positive emotions. Evidence is collapsed into a `<details>`, with a list of links in words underneath.

**Segment column.** Header "Segment N. Name", `intro` below it, then cards in ascending `n` order, then copies of jobs from `also_segments` at the end.

**Links.** Drawn over the columns in SVG, from the cards' real coordinates:
- `seq` — solid orange, with an arrow;
- `part` — dashed teal, with an arrow;
- a copy of a job in another segment — grey dots, no arrows.

Vertically adjacent cards in a column connect bottom-to-top; distant ones in the same column route around it on the left (`seq`) or right (`part`); cards in different columns connect horizontally. Hovering a line shows its `basis` in a tooltip — that's how you check which links rest on an "AI-assumption".

**Segment map** per `references/segment-map-nmt.md`: price, a "Competing / Not competing" badge, the segment's goal, a list of its jobs with circles by `fit`. Competing cards come first and are tan. `"strict_two_states": true` in `project` draws `min` as an empty circle.

**Orange text** appears wherever `[AI-ASSUMPTION]` shows up in the data. This is done by substitution after escaping, so the label can't accidentally arrive from the data itself.

## What the page can do

- Checkboxes in the sticky bar toggle each kind of link on and off independently.
- Clicking a card leaves only its links visible and dims the rest; clicking again clears the selection.
- The search box hides cards whose text doesn't contain the typed substring; links to hidden cards aren't drawn.
- "Reset" returns everything to its starting state.
- Printing to PDF from the browser: the control bar hides, cards don't break across pages.

## Limits to tell the user about

- **Cards can't be dragged around or commented on.** This is a static page. The source of truth is `jobs.json`; whatever needs to change gets changed there and redrawn.
- **Edits made to the HTML itself will be overwritten** by the next redraw. Never edit the generated file.
- **Columns of very different heights are normal.** If one segment has 40 jobs and another has 3, lines between distant cards get long. `--only` helps while you're working through one segment.
- **The file is self-contained:** no external requests, no fonts, no CDN. Opens from disk, works offline, ships as one file.
- **Size.** 50 jobs and 69 links come out to roughly 110 KB. A browser will handle hundreds of jobs too, but the links get visually dense — toggle kinds off, or look at one job at a time via a click.

## If something went wrong

| Symptom | Cause | What to do |
|---|---|---|
| No lines at all | `edges` is empty in `jobs.json`, or `--no-graph` is set | fill in `edges` (stage 6) |
| A line runs through a card | two cards in the same column are far apart and connected via their neighbors | acceptable; can be spread out by changing the jobs' `n` |
| Too much is colored orange | some text in the data happens to match the label | check the field: the `[AI-ASSUMPTION]` label should only come from your own conclusions |
| The segment map is empty, or every circle is empty | `goal`/`price`/`compete` and `fit` aren't filled in | stages 7 and 8 |
| The script crashes with `KeyError` | `jobs.json` didn't pass the validator | `python3 scripts/validate_jobs.py work/jobs.json` |
