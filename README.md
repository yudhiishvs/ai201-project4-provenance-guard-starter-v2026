# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **Unit 7 is documented below.** The later sections are reserved for Unit 8.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

Provenance Guard is a local Flask service a writing site can call for a cautious
authorship signal. Its output is an automated guess, not proof of who wrote a
piece.

1. `POST /submit` receives a JSON object with `text` and `creator_id`.
2. The route checks field types, blank values, and size limits. Rejections get
   JSON 400/413 responses and audit events without running the model.
3. A valid piece gets a UUID `content_id` for tracking and appeals.
4. `detector.py::model_signal` measures how predictable the wording is to the
   local GPT-2 model; `stylometry.py::style_signal` measures the text's shape.
5. `scoring.py::combine_signals` joins those readings into a 0–1 score. The
   response calls it `confidence`, but it is an **AI-likelihood axis**, not a
   calibrated probability or a guarantee of authorship.
6. `scoring.py::score_to_label` maps that score to `human`, `unsure`, or `ai`
   and a full sentence a reader can understand.
7. The route appends the decision and both input scores to `logs/audit.jsonl`
   and returns them as JSON. `POST /appeal` later appends an `under_review`
   event with the writer's reasoning; the original decision remains intact.

`POST /submit` accepts nonblank strings, with `text` capped at 10,000 characters
and `creator_id` at 128. A text too short for GPT-2 to score returns JSON 400;
a missing local model returns JSON 503. `POST /appeal` takes `content_id` and
nonblank `reasoning` of at most 2,000 characters; an unknown id returns 404.
The latest audit event for an id is its current status. This demo has no login
system, so a caller who knows an id can appeal it; a real site must check the
writer's identity before exposing this route.

---

## Signals and Scoring

### Signal one — the model signal

**What it measures:** `detector.py::model_signal` uses GPT-2 perplexity to
measure how predictable the word sequence is in context. Lower perplexity
produces a higher AI-likelihood signal. It loads the model once and keeps it
in memory.

**Why that might differ between human and AI writing:** Generated prose often
uses high-probability continuations, so a language model may predict it well.

**What it can't see:** Predictability is not authorship. A person writing in
plain language or repeating familiar wording can score high; edited AI text
or unusual generated prose can score low. It cannot see drafting history or
whether a human selected the words.

### Signal two — the style signal

**What it measures:** `stylometry.py::style_signal` uses three shape features:
sentence-length spread (standard deviation divided by mean), word variety
(unique words divided by words in a fixed 40-word window), and expressive
punctuation marks per word. Their AI-like components are weighted 0.40, 0.40,
and 0.20. A piece under 20 words gets a neutral style score of 0.5 because
these measures are unstable on a short poem.

**Why that might differ between human and AI writing:** Repeated vocabulary,
regular sentence lengths, and sparse punctuation can make generated prose look
more uniform than an individual writer's work.

**What it can't see:** It has no understanding of meaning or authorship. A
human can intentionally write uniform sentences; an AI user can add a few
breaks, uncommon words, or punctuation marks to move the score. Word variety
still depends on length despite the fixed window.

### The combining rule

**The rule:** `scoring.py::combine_signals` takes a weighted average. If the
signals differ by at least 0.35, it halves the result's distance from 0.5, so
conflicting evidence tends toward the unsure label.

**The numbers:** Model weight 0.60; style weight 0.40; disagreement gap 0.35;
disagreement shrink 0.50. `config.py` holds these and the label boundaries:
`HUMAN_THRESHOLD = 0.30`, `AI_THRESHOLD = 0.75`. The style feature scales are
in `stylometry.py`: spread divided by 0.70, variety mapped from 0.90 down over
a 0.40 range, and punctuation density divided by 0.15.

**Where it lives:** `scoring.py::combine_signals`.

**A split case:** A formal human passage from the Declaration of Independence
scored 0.8478 on the model signal and 0.2406 on style. The weighted average
was 0.6049; the disagreement rule moved it to 0.5525, so it received
`unsure` instead of an AI accusation. A high model score on this passage
shows why predictability alone cannot establish authorship.

These are the four initial calibration readings. The AI examples were written
for this run; the human passages are from the [Gettysburg Address (NPS)](https://www.nps.gov/linc/learn/historyculture/gettysburgaddress.htm)
and the [Declaration of Independence (National Archives)](https://www.archives.gov/founding-docs/declaration-transcript).

| Input | Model | Style | Combined | Guess |
|---|---:|---:|---:|---|
| AI-generated library paragraph | 0.8663 | 0.4330 | 0.5965 | unsure |
| Gettysburg Address excerpt | 0.7164 | 0.2483 | 0.5146 | unsure |
| Declaration excerpt (formal human writing) | 0.8478 | 0.2406 | 0.5525 | unsure |
| Lightly edited AI library paragraph | 0.7265 | 0.1825 | 0.5045 | unsure |

The outer labels are reachable on actual text: the deliberately repetitive
AI example scored 0.9977 through `POST /submit` (`ai`), while a passage from
Lewis Carroll's [Jabberwocky](https://www.gutenberg.org/files/12/12-h/12-h.htm)
scored 0.2038 (`human`). Those are edge cases, not evidence of general
detection accuracy.

---

## Label Variants

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 ≤ score ≤ 0.30 | Our checks found stronger signs of human writing. This automated result cannot prove who wrote it. |
| unsure | 0.30 < score < 0.75 | Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal. |
| high-confidence AI | 0.75 ≤ score ≤ 1.00 | Our checks found strong signs of AI-generated writing. This automated label may be wrong, and the creator can appeal it. |

The unsure text explicitly avoids accusing a writer when the evidence splits,
and it tells them an appeal is available. All scores from 0.00 to 1.00 map to
exactly one of these labels.

---

## Sample Run

A real local GPT-2 request on November 4, 2026. The exact JSON response and
append-only audit events are pasted below. The first model call loads the
weights; later submissions reuse them.

**A submission**

```bash
$ curl -sS -X POST http://127.0.0.1:5000/submit \
  -H 'Content-Type: application/json' \
  -d '{"text":"The system works well. The system works well. The system works well. The system works well. The system works well. The system works well.","creator_id":"demo-writer"}'
```

```json
{"confidence":0.9923,"content_id":"8a9311fb-224d-4cf7-be9f-e892855811a3","guess":"ai","label":"Our checks found strong signs of AI-generated writing. This automated label may be wrong, and the creator can appeal it.","model_score":0.9872,"status":"decided","style_score":1.0}
```

**An appeal**

```bash
$ curl -sS -X POST http://127.0.0.1:5000/appeal \
  -H 'Content-Type: application/json' \
  -d '{"content_id":"8a9311fb-224d-4cf7-be9f-e892855811a3","reasoning":"Please review this result; the repetition was intentional."}'
```

```json
{"content_id":"8a9311fb-224d-4cf7-be9f-e892855811a3","message":"Your appeal was recorded for human review.","status":"under_review"}
```

**What the log showed afterwards**

```bash
$ curl -sS 'http://127.0.0.1:5000/log?limit=2'
```

```json
{"count":2,"entries":[{"combined_score":0.9923,"content_id":"8a9311fb-224d-4cf7-be9f-e892855811a3","creator_id":"demo-writer","guess":"ai","label":"Our checks found strong signs of AI-generated writing. This automated label may be wrong, and the creator can appeal it.","model_score":0.9872,"status":"decided","style_score":1.0,"timestamp":"2026-11-04T22:48:12+00:00"},{"content_id":"8a9311fb-224d-4cf7-be9f-e892855811a3","creator_id":"demo-writer","event":"appeal","reasoning":"Please review this result; the repetition was intentional.","status":"under_review","timestamp":"2026-11-04T22:48:18+00:00"}]}
```

---

## How I Used AI

**Moment 1**

- **What I asked for:** I attached the Provenance Guard brief and said,
  “Do this.”
- **What came back:** The response outlined the submission flow, both signals'
  blind spots, and the appeal path.
- **What I changed:** The starter's blank `criteria.md` became five checkable
  targets, and `planning.md` captured the submission path and the false-positive
  appeal path. Both were committed before model results.

**Moment 2**

- **What I asked for:** “Just do the assignment yourself in its entirety.”
- **What came back:** Codex implemented both signals, three labels, the two
  routes, and tests. Its first four calibration cases all received `unsure`;
  a repetitive AI example and a Carroll poem reached the outer labels.
- **What I changed:** The service now records both signal scores and every
  appeal in an append-only log. I kept the conservative thresholds and added
  the measured disagreement case and the real curl transcript above, rather
  than claiming the detector was accurate.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** 10 submissions per minute and 200 per day.

**Why those numbers and not others:** A writer can revise and submit several
times in a minute, while the eleventh attempt in that minute is more likely to
be an automated burst. A 200/day cap leaves room for a long writing session but
stops one identity from sending a thousand variants in a day. The limiter uses
in-memory counters, so restarting this local demo resets them.
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** A nonblank `creator_id` is the key; requests
without one fall back to the caller's address. This lets writers sharing an
address submit independently, but a script can evade the limit by inventing
creator IDs. A real service would bind IDs to authenticated accounts.

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```
200 200 200 200 200 200 200 200 200 200 429 429 429 429 429
```

`run_attacks.py --flood 15 --creator milestone1-flood` produced this on
November 13, 2026. `GET /health` returned `"rate_limiting":true`, and
`GET /log` showed rejection events with `reason:"rate_limited"`. A decided
entry includes timestamp, content ID, creator ID, guess, both signal scores,
combined score, reader label, and status; a 429 has no decision scores because
the route did not score it.

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
