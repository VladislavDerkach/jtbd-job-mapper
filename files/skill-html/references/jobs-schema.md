# `work/jobs.json` schema

One file holds everything: the project, segments, jobs, links, product-fit rating. The scripts in `scripts/` read only this file. Example: `assets/jobs.example.json`.

```jsonc
{
  "project": {
    "title": "Jobs of yachting-industry user segments",
    "product": { "name": "HandoverBoat", "state": "what it does today + how that's known" },
    "sources": [
      { "id": "S1", "title": "Desk research: charter-base staff", "kind": "desk" },
      { "id": "S2", "title": "Corpus: 20 yachting chats, 107,797 messages", "kind": "corpus" }
    ],
    "legend": ["optional lines of legend for the board"]
  },

  "segments": [
    {
      "id": "base",                       // latin, unique
      "n": 1,                             // column order on the board
      "name": "Base (charter operator)",
      "intro": "optional paragraph under the column header",
      // filled in at stage 8:
      "goal": "Do a fleet handover fast and without deposit disputes",
      "goal_basis": "graph | AI-assumption",
      "price": "$$$$",                    // $ … $$$$
      "compete": true                     // the product covers at least one job right now
    }
  ],

  "jobs": [
    {
      "id": "J1",                         // unique, never changes once assigned
      "n": 1,                             // card number on the board
      "segment": "base",
      "also_segments": [],                // same job in other segments (copies on the board)
      "type": "b2c",                      // b2c | b2b-business | b2b-personal
      "job_type": "regular",              // regular | orientation | tax | fake | emotional | viral
      "pair_of": null,                    // for b2b-personal: the business job's id
      "title": "Hand over the fleet fast, with an act no one disputes",
      "who": "base, mid-size and fleet. Roles: manager, technician.",
      "basis": "corpus and desk.",
      "when": {
        "context": ["point 1 (corpus)", "point 2 (desk)"],   // string or list
        "trigger": "boat return or client arrival",
        "neg": "handover stress (desk); fear of disputes (hypothesis)",
        "cs": "paper check-in/check-out checklist (corpus)"
      },
      "want": "I want to do a fast handover, with an act no one will dispute",
      "criteria": ["faster than the paper checklist", "act signed by both sides"],
      "criteria_label": null,             // your own label instead of "Success criteria:"
      "why": "not lose handover time and not get deposit disputes",
      "pos": "peace of mind [AI-assumption]",
      "evidence": [ { "source": "S2", "quote": "…", "where": "chat X, 2024-12" } ],
      // stage 7:
      "fit": null,                        // now | min | none | null
      "fit_note": ""
    }
  ],

  "edges": [
    { "from": "J2", "to": "J3", "kind": "seq",  "basis": "S1: cycle stages" },
    { "from": "J2", "to": "J1", "kind": "part", "basis": "AI-assumption" }
  ]
}
```

## Rules

- Any text field with no data = `"—"`. Empty strings and `null` in description fields are forbidden (the validator catches them).
- `context`, `cs`, `criteria` can be a string or a list. A list renders as nested bullets.
- `edges.kind`: `seq` (sequence in time, arrow from earlier to later) or `part` (the lower job is done for the sake of, or as part of, the upper one; arrow from lower to upper).
- `n` can be renumbered; `id` cannot — links reference `id`.
- `type` is about the deal side (B2C, business job, decision-maker's personal job). `job_type` is about the canonical job type (regular, orientation, Tax, Fake, emotional, viral). The fields are independent — a decision-maker's personal job can also be `job_type: "tax"`. Selection rules live in `extraction-rules.md`.
- `want` must be in "I want to + infinitive" form, with exactly one verb; `why` is one higher-level job, also an infinitive. The validator treats a violation as an error, not a warning (rules and examples in `job-format.md`).
