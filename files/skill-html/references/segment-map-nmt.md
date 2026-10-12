# Segment map, Next Move Theory canon

## What it is

The map shows which segments the product competes in, and which of that segment's jobs it covers. A segment here is defined by the customer's shared job ("Take the family on a budget-friendly Thailand vacation"), not by demographics.

## The segment card

Top to bottom:
1. **Price**: `$` … `$$$$`, the size of money the customer spends on the whole segment job (not your product's price).
2. **Badge**: "Competing" or "Not competing".
3. Small caption: the segment's number and name from the job board (to link the map back to the cards).
4. **Headline**: the segment's top-level job, in the customer's words.
5. **List of the segment's jobs**, with circles:
   - filled blue: the product covers it now (`fit: now`);
   - light with a blue ring: with minimal extra work (`fit: min`);
   - empty: doesn't cover it (`fit: none`).

Competing cards are tan; the rest are white with a tan border. Competing ones come first.

In the original canon the circles have two states; the skill adds a third (light) to show the nearest next steps. If the user wants strict canon, set `"strict_two_states": true` in `project` and `min` draws as an empty circle.

## How to fill it in

- **goal**: take the segment's top job on the graph (the one with no outgoing `part`) and rephrase it as the segment's goal. If there's no top job, write your own and set `goal_basis: "AI-assumption"`; on the map that becomes a footnote.
- **price**: estimate from the money in the research (deposits, service cost, damages). If there are no numbers, say so in the map's legend — it's a hypothesis.
- **compete**: `true` if at least one of the segment's jobs has `fit: now`. The user can set a different rule (e.g. "we're targeting this segment"); if so, write their rule into the legend.
- Job list: every job in the segment, copies from `also_segments` included.

## After building it

Take a screenshot, check that no card is cut off and the circles match `fit`. In your reply to the user, list: which segments compete, which prices and goal statements are hypotheses, which rules you applied.
