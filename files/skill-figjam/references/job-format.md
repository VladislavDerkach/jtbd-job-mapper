# Job format (Advanced JTBD + Next Move Theory, Ivan Zamesin)

## Structure

A job is described in three blocks.

**When** (the situation that starts the customer's movement):
- **Context**: who the customer is and what circumstances they're in.
- **Trigger**: the event after which "I have to act now".
- **Negative emotions**: what the customer feels before deciding.
- **Consideration Set**: what they're choosing between, and why they prefer what they prefer.

**Want** (the job itself):
- A statement of the progress the customer is after, starting with "I want to …".
- Followed by **an infinitive, exactly one**: "I want to hand over the boat", "I want to get my deposit back". Each infinitive is a separate job.
- **Success criteria**: how the customer will know the job is done.

**So that** (why):
- **One** higher-level job, and it's a job too: an infinitive, not a noun. "So that I stop getting deposit disputes."
- **Arrive at positive emotions**: the emotional payoff, mirroring the negative emotions from "When".

## Wording rules

`scripts/validate_jobs.py` checks these, and they're errors, not warnings: a wrongly worded job breaks every later stage.

| Rule | Not allowed | Allowed |
|---|---|---|
| Infinitive verb, not a noun | "Fleet management" | "I want to manage the fleet" |
| Subject is the person doing the job | "I want there to be documents" | "I want to answer with a document, not words" |
| Exactly one verb | "I want to hand over the boat and get the deposit back" | two jobs: "I want to hand over the boat" and "I want to get the deposit back", linked by `part` |
| Present-looking-forward, not already-resolved | "I want everything to already be settled" | "I want to resolve it" |

- **Several verbs in one line is not one job — it's a stack of jobs.** Break it apart by level: what's done for the sake of what. Goals chained with "and" are the most common mistake, and it's the one that breaks the segments and the graph downstream.
- **Constraints go into the success criteria, not into the wording.** "Fast," "without stress," "under $X" are criteria. The job statement keeps only the verb and what it applies to.

## B2C and B2B

- **B2C:** one customer job. Positioning and product can be noted above the description (example: "Guaranteed to learn German" → product "online German courses").
- **B2B:** one product gets two jobs described:
  - **the business job** (the company's functional requirements);
  - **the decision-maker's personal job** (why this exact choice; Zoom example: "won't have to justify it to the CEO").
  In `jobs.json` these are two records: `b2b-business` and `b2b-personal` with a `pair_of` field.

## Honesty rules

This is the main thing. Every field value belongs to exactly one of four kinds.

| Kind | How to write it | Example |
|---|---|---|
| Fact from a source | text + source label in parentheses | "about three check-ins per Saturday per technician (corpus)" |
| The research author's hypothesis | text + "(hypothesis)" | "fear of boat-condition disputes (hypothesis)" |
| Your own assumption | text + "[AI-ASSUMPTION]" | "fear of losing the client [AI-ASSUMPTION]" |
| No data | "—" | — |

- Source labels: `corpus` (customer voice: chats, interviews, reviews), `desk` (market description without customer voice), `author` (the job was named by the user themself), or a short source name.
- Only add AI assumptions if the user agreed to fill the gaps. Even then, don't fill in everything — assume only where there's at least indirect support, and name it briefly.
- An uncertain but present piece of data gets written as-is, with its source label. Don't throw it out.
- Don't rephrase customer quotes to sound nicer. If the wording is from the corpus, keep the customer's own words in quotes "…".
- Carry numbers with their source. If a number has no primary source, say so in `basis`.

## Card fields beyond the blocks

- **Number and title**: a short job statement without "I want to" (up to 80 characters).
- **Segment**: who does the job (role and subtype, e.g. "small, mid-size and fleet operators; manager, technician").
- **Basis**: where the job came from and how confirmed it is. Also goes here: mention frequency, Fake Job signals, related jobs.

## Example (B2B, abridged)

```
1. Do a shift handover with an act no one disputes
Segment: small, mid-size and fleet charter operators. Roles: manager, technician.
Basis: corpus and desk.

When:
  • Context:
      – season April–October, one shift-handover day: Saturday
      – about three check-ins per Saturday per technician (corpus)
  • Trigger: boat return or client arrival
  • Negative emotions: handover stress (desk); fear of disputes (hypothesis)
  • Consideration Set: paper checklist; digital checklists at large operators (desk)
Want to do a shift handover with an act no one will dispute
  • Success criteria:
      – faster than the paper checklist
      – act signed by both sides
So that I stop getting deposit disputes after Saturday handovers
  • Arrive at positive emotions: peace of mind that no complaint will land after Saturday [AI-ASSUMPTION]
```
