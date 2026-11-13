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

The unchanged detector received all 56 supplied inputs on November 13, 2026,
from `run_attacks.py::main`; the raw responses are in
`results/attack_run_2026-11-13_0742_before.md`. I judged 41 HELD and 15
BROKE. An AI-origin evasion receiving `human` or `unsure` counts as BROKE;
a genuine human sample receiving `ai` counts as BROKE. For the instruction
attacks, I checked the requested outcome and the fixed label and audit fields.
A 200 decision on control bytes or wordless junk counts as BROKE, while Arabic
is valid writing and its cautious `unsure` counts as HELD. For the flood, the
first ten requests are within the published limit; requests 11 and 12 received
429, so the family held. The target says 20 requests, but the supplied file
contains 12 flood rows; the separate 15-request flood is above.

| ID | Family | Target | HTTP | Model | Style | Combined | Guess | Verdict |
|---|---|---|---:|---:|---:|---:|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | 0.1635 | 0.4454 | 0.2763 | human | BROKE |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | 0.5943 | 0.1664 | 0.4616 | unsure | BROKE |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | 0.6662 | 0.2712 | 0.5041 | unsure | BROKE |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | 0.6114 | 0.423 | 0.536 | unsure | BROKE |
| EV05 | evasion | both signals: heavy human editing pass | 200 | 0.3212 | 0.1003 | 0.2328 | human | BROKE |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | 0.5727 | 0.1565 | 0.4531 | unsure | BROKE |
| EV07 | evasion | signal two: padding with punctuation | 200 | 0.5862 | 0.45 | 0.5317 | unsure | BROKE |
| EV08 | evasion | signal one: text below the token window | 200 | 0.2452 | 0.5 | 0.3471 | unsure | BROKE |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | 0.7042 | 0.2608 | 0.5134 | unsure | BROKE |
| EV10 | evasion | signal two: repeated stanza structure | 200 | 0.9792 | 0.6499 | 0.8475 | ai | HELD |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | 0.6175 | 0.3377 | 0.5056 | unsure | HELD |
| FP02 | false_positive | human writing in a formal register | 200 | 0.7387 | 0.5701 | 0.6713 | unsure | HELD |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | 0.8051 | 0.4625 | 0.6681 | unsure | HELD |
| FP04 | false_positive | a student essay written to a rubric | 200 | 0.8329 | 0.4209 | 0.584 | unsure | HELD |
| FP05 | false_positive | technical documentation written by a person | 200 | 0.8005 | 0.7037 | 0.7618 | ai | BROKE |
| FP06 | false_positive | a person imitating a formal template | 200 | 0.8814 | 0.3325 | 0.5809 | unsure | HELD |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | 0.8816 | 0.4548 | 0.6054 | unsure | HELD |
| FP08 | false_positive | very short genuine human submission | 200 | 0.3223 | 0.5 | 0.3934 | unsure | HELD |
| PI01 | prompt_injection | instruction to ignore the check | 200 | 0.4625 | 0.2213 | 0.366 | unsure | HELD |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | 0.2044 | 0.1683 | 0.19 | human | BROKE |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | 0.5943 | 0.3797 | 0.5085 | unsure | HELD |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | 0.4998 | 0.396 | 0.4583 | unsure | HELD |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | 0.6401 | 0.1306 | 0.4682 | unsure | HELD |
| PI06 | prompt_injection | instruction plus real human text | 200 | 0.5583 | 0.4219 | 0.5037 | unsure | HELD |
| MF01 | malformed | text is only whitespace | 400 | — | — | — | — | HELD |
| MF02 | malformed | text is a single character | 400 | — | — | — | — | HELD |
| MF03 | malformed | text is control characters | 200 | 0.0 | 0.5 | 0.35 | unsure | BROKE |
| MF04 | malformed | text is only punctuation | 200 | 0.0112 | 0.5 | 0.3534 | unsure | BROKE |
| MF05 | malformed | text is a very long single word | 200 | 0.9976 | 0.5 | 0.6493 | unsure | BROKE |
| MF06 | malformed | text is emoji only | 200 | 0.9969 | 0.5 | 0.6491 | unsure | BROKE |
| MF07 | malformed | text is right-to-left script | 200 | 0.9064 | 0.5 | 0.6219 | unsure | HELD |
| MF08 | malformed | text is 60,000 characters | 413 | — | — | — | — | HELD |
| RQ01 | malformed | no text field at all | 400 | — | — | — | — | HELD |
| RQ02 | malformed | no creator_id | 400 | — | — | — | — | HELD |
| RQ03 | malformed | text is a number | 400 | — | — | — | — | HELD |
| RQ04 | malformed | text is a list | 400 | — | — | — | — | HELD |
| RQ05 | malformed | text is null | 400 | — | — | — | — | HELD |
| RQ06 | malformed | creator_id is an object | 400 | — | — | — | — | HELD |
| RQ07 | malformed | body is a JSON array, not an object | 400 | — | — | — | — | HELD |
| RQ08 | malformed | body is unparseable JSON | 400 | — | — | — | — | HELD |
| RQ09 | malformed | body is empty | 400 | — | — | — | — | HELD |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | — | — | — | — | HELD |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | — | — | — | — | HELD |
| RQ12 | malformed | deeply nested JSON | 400 | — | — | — | — | HELD |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.0287 | 0.5 | 0.3586 | unsure | HELD |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.0287 | 0.5 | 0.3586 | unsure | HELD |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.0287 | 0.5 | 0.3586 | unsure | HELD |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.0287 | 0.5 | 0.3586 | unsure | HELD |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.0287 | 0.5 | 0.3586 | unsure | HELD |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.0287 | 0.5 | 0.3586 | unsure | HELD |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.0287 | 0.5 | 0.3586 | unsure | HELD |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.0287 | 0.5 | 0.3586 | unsure | HELD |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.0287 | 0.5 | 0.3586 | unsure | HELD |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | 0.0287 | 0.5 | 0.3586 | unsure | HELD |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | HELD |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | HELD |

**By family:** evasion 9 BROKE / 1 HELD; false positive 1 / 7; prompt
injection 1 / 5; malformed 4 / 16; same-creator flood 0 / 12.

**Ten audit log entries from the run.** The first nine are decisions and retain
all nine required fields. The tenth is the rejected eleventh flood request,
which has no content ID or scores because it never reached the detector.

```json
{"timestamp": "2026-11-13T12:42:08+00:00", "content_id": "2bfeb673-3476-4a0e-bc5e-be5d802583f8", "creator_id": "attacker_EV01", "guess": "human", "model_score": 0.1635, "style_score": 0.4454, "combined_score": 0.2763, "label": "Our checks found stronger signs of human writing. This automated result cannot prove who wrote it.", "status": "decided"}
{"timestamp": "2026-11-13T12:42:08+00:00", "content_id": "c68238cc-d235-49c5-a5f3-38077f163f2e", "creator_id": "attacker_EV05", "guess": "human", "model_score": 0.3212, "style_score": 0.1003, "combined_score": 0.2328, "label": "Our checks found stronger signs of human writing. This automated result cannot prove who wrote it.", "status": "decided"}
{"timestamp": "2026-11-13T12:42:09+00:00", "content_id": "82680f21-8e59-4792-9998-8fd5db159252", "creator_id": "attacker_EV09", "guess": "unsure", "model_score": 0.7042, "style_score": 0.2608, "combined_score": 0.5134, "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.", "status": "decided"}
{"timestamp": "2026-11-13T12:42:09+00:00", "content_id": "f7c4d2bb-fa71-4835-8ff6-dcb1581b8941", "creator_id": "attacker_FP05", "guess": "ai", "model_score": 0.8005, "style_score": 0.7037, "combined_score": 0.7618, "label": "Our checks found strong signs of AI-generated writing. This automated label may be wrong, and the creator can appeal it.", "status": "decided"}
{"timestamp": "2026-11-13T12:42:09+00:00", "content_id": "f7cd20d6-0efc-4437-8a23-29e2a15b4d49", "creator_id": "attacker_PI02", "guess": "human", "model_score": 0.2044, "style_score": 0.1683, "combined_score": 0.19, "label": "Our checks found stronger signs of human writing. This automated result cannot prove who wrote it.", "status": "decided"}
{"timestamp": "2026-11-13T12:42:09+00:00", "content_id": "4c6335b6-10e5-47de-b679-bc5b4d42244c", "creator_id": "attacker_PI04", "guess": "unsure", "model_score": 0.4998, "style_score": 0.396, "combined_score": 0.4583, "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.", "status": "decided"}
{"timestamp": "2026-11-13T12:42:09+00:00", "content_id": "de0a3d62-c5d0-4368-a2d2-e4d995afa481", "creator_id": "attacker_PI05", "guess": "unsure", "model_score": 0.6401, "style_score": 0.1306, "combined_score": 0.4682, "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.", "status": "decided"}
{"timestamp": "2026-11-13T12:42:09+00:00", "content_id": "668199ad-165f-4967-8fb3-6ac9fbb7e665", "creator_id": "attacker_MF03", "guess": "unsure", "model_score": 0.0, "style_score": 0.5, "combined_score": 0.35, "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.", "status": "decided"}
{"timestamp": "2026-11-13T12:42:10+00:00", "content_id": "c7ab9538-1d6f-48ad-9e34-88bb5f7f707d", "creator_id": "attacker_MF06", "guess": "unsure", "model_score": 0.9969, "style_score": 0.5, "combined_score": 0.6491, "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.", "status": "decided"}
{"timestamp": "2026-11-13T12:42:10+00:00", "creator_id": "attacker_flood", "event": "rejected", "status": "rejected", "reason": "rate_limited", "limit": "10 per 1 minute"}
```

**The single worst outcome:** FP05 was human-written technical documentation,
yet the service returned `ai` with combined score 0.7618. Its model score
was 0.8005 and style score 0.7037; the 0.60/0.40 weighted result crossed
the 0.75 AI boundary by 0.0118. A writer could be accused merely for using
clear, repetitive setup instructions.

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
