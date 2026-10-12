# How to extract jobs from research

## 1. Identify the source type

| Type | What it is | What you can extract | Label |
|---|---|---|---|
| Customer voice | chats, forums, interviews, reviews, call transcripts | jobs, triggers, emotions, customer wording, frequencies | `corpus` / `interview` |
| Market description | desk research, overviews, job postings, reports | roles, processes, KPIs, contract models, numbers | `desk` |
| User's own words | jobs the PM named themself | the job's wording | `author` |

Desk research describes how a process works, but it doesn't prove anyone has a job and is willing to pay for it. A job sourced only from desk gets a note in "Basis" that there's no customer voice behind it.

## 2. Look for jobs, not features

Signs of a job in the text:
- a request for help, "how do I", "where do I find", "how much does it cost", "who can";
- a complaint about lost money or time, a conflict, a dispute;
- a process description with ownership attached ("I'm responsible for…", a role's KPI);
- a homemade workaround (their own checklist, spreadsheet, phone photos).

Word the job as the customer's progress ("Get the deposit back without a dispute"), not as a product feature ("Take photos of the damage"), unless the customer themself talks about the means.

## 3. Collect evidence for each job

In `evidence`, put short quotes (up to 25 words) or exact numbers with their source and location. If there's no quote, only a count or a paraphrase, say so.

Useful signals of a job's strength (fill into "Basis" when the data exists):
- **money**: did they pay for a solution, how much;
- **frequency**: how often it comes up (once a year vs. every Saturday);
- **word**: does the customer have a fixed word for this job;
- **channel**: where do they go looking for a solution.

## 4. Job type

Assign every job a `job_type`. Default is `regular`. The other types change product decisions, so tell them apart.

**`fake` — Fake Job.** A future-tense intention with zero past investment behind it. One diagnostic question: **has this person ever done anything in the past to get this outcome — spent money, spent time, spent effort?** If they haven't done anything, it's likely a fantasy, and you can't build a product on it: it looks like a real segment, scores fine in a market sizing exercise, and converts to near zero.

What does **not** define a Fake Job:
- **Not frequency.** A once-a-year job can be entirely real. Frequency is a separate property that sets unit economics (how many times a year this can be sold), not whether the job is real.
- **Not the absence of payment to our solution specifically.** Look at whether they paid anyone — a substitute, insurance, their own time, a homegrown workaround. Money that went to a competitor or substitute is proof the job exists.
- If there's no past investment but the topic is clearly alive, go up a level — there's often a real higher-level job above the fantasy. File that one separately, and keep the fantasy in its own bucket of hypotheses, not in the working list.

**`tax` — Tax Job.** Unplanned work the person does only because a solution they hired failed to do its part. Corpus signals: "I had to do it myself", redoing something, finishing up after a vendor, a post-deal dispute, a repeat visit. Look for these specifically: they hit retention harder than an equal-size benefit helps it, and this is the exact moment when the person is open to switching.  File it as its own job, and in "Basis" note which solution broke.

**`orientation` — a "figure out and pick a solution" job** ("understand how this is usually done", "choose who to hand this to"). Useful for the Consideration Set and for content.

**`emotional` — the expected outcome is an emotional shift** ("stop being afraid of a dispute", "feel at ease"). This job has no higher-level job: it's terminal, put "—" in `why`.

**`viral` — a job the person does for or with someone else.** Flag it: it brings in people who never bought anything themselves.

Separately from the type, mark a job's strength as "weak" in "Basis" when evidence is thin: one mention, no customer word for it, no past investment.

## 5. Segmentation

- A segment is defined by role, circumstances and money at stake — not by demographics.
- If different circumstances inside one role change the job (a small operator vs. a fleet), note it in the card's "Segment"; create a separate segment only if the job itself changes.
- The payer and the user can be different segments. Note who pays, if the data shows it.
- In B2B, look for the decision-maker: who picks the tool and who they answer to.

## 6. What to return

A `jobs.json` fragment (schema in `jobs-schema.md`): segments, jobs, links that are directly visible in the source (e.g. "step 2 follows step 1" in a process description). Plus a short list of "source takeaways": 3–5 points that didn't become jobs but matter for the product (e.g. "the payer should probably change").
