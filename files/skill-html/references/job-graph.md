# The job graph — connections between jobs

## Two kinds of links

| Kind | `kind` | When to use it | On the board |
|---|---|---|---|
| Sequence | `seq` | job B usually follows job A right away (steps of one process, stages of a cycle) | solid orange arrow A → B |
| Level | `part` | job A is done for the sake of job B, or is part of it | dashed teal arrow from the lower A to the higher B |

A third kind is drawn automatically: if a job has `also_segments`, its copies in other columns are joined by a grey dotted line with no arrows ("the same job in another segment") and labeled "Alternative User Segment".

## How to find links

- Pull **sequence** from process descriptions: "after checkout, the manager calculates damage", step chains in desk research, chronology in customer stories.
- Look for **level** by asking "what for?": one job's "So that" field often matches another job's "I want to". The decision-maker's personal job is almost always above the business jobs.
- Don't connect everything to everything. A job with no links is normal — it's often a signal it stands apart (frequently a Fake Job or a different market).
- Only link jobs across segments when one segment's job directly serves another's. Mirror jobs (the same problem seen from both sides of a deal) get a note in `basis`, not a `part` link.
- Write a `basis` for every link: where it comes from. If it's your own conclusion, write "AI-assumption".

## Arrow direction

Keep one rule for the whole board: `part` always points from the lower job to the higher one. A user editing the board by hand may break this rule; when reading the board back (stage 6), judge the level by the jobs' meaning, and name any direction mismatch to the user in one line rather than silently fixing it.

## Layout

The script lays links out so lines don't cross cards: vertically adjacent cards in a column connect bottom-to-top, distant ones in the same column route around it on the left (`seq`) or the right (`part`), cards in different columns connect automatically. If many lines converge on one card, they merge near its edge — that's acceptable; the user can spread them apart by hand.
