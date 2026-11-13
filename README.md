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
> **Units 7 and 8 are documented below.**

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
`HUMAN_THRESHOLD = 0.30`, `AI_THRESHOLD = 0.80` after the Unit 8 improvement
(initially 0.75). The style feature scales are
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
| unsure | 0.30 < score < 0.80 | Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal. |
| high-confidence AI | 0.80 ≤ score ≤ 1.00 | Our checks found strong signs of AI-generated writing. This automated label may be wrong, and the creator can appeal it. |

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

**Moment 3 — Unit 8**

- **What I asked for:** I asked Codex to complete the testing assignment in
  the existing repo locally and supplied the staff attack zip and a zip of
  evaluation samples.
- **What came back:** Codex enabled the prepared limiter, froze ten generated
  AI samples and the supplied personal samples, ran the full attack set and
  fifteen criterion trials before and after one threshold change, and wrote
  runner tests, reports, and this analysis.
- **What I kept in the submission:** The original five targets stayed
  unchanged. Codex inspected the attack text only after the initial full run.
  The personal samples are user-supplied, not independently verified. This
  report keeps the two missed criteria and fourteen remaining attacks visible,
  and the detector improvement is confined to the AI boundary from 0.75 to
  0.80.

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

`scenarios.py` froze five sets before the first criterion run. The 20 files in
`samples/evaluation_samples/` were supplied as the student's own writing;
`personal_01` through `personal_05` are deliberately plain, and every piece
has 119–129 words. I did not independently verify authorship. The ten
95–107-word AI samples in `samples/ai_generated.json` were generated by Codex
before this evaluation, not selected from the observed staff attacks. The
12-piece label set mixes those sources, a repetitive AI edge case from Unit 7,
and a short human-authored [Lewis Carroll passage](https://www.gutenberg.org/files/12/12-h/12-h.htm).
The same inputs and service settings were used for all three trials.

| Criterion | Original target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Human writing false accusations | ≤1 AI of 20 | 0/20 | 0/20 | 0/20 | **MET** |
| 2. AI score median above human | gap ≥0.15 | −0.0729 | −0.0729 | −0.0729 | **MISSED** |
| 3. Three labels on ≥12 pieces; complete 101-score grid | 3/3 and 101/101 | 2/3; 101/101 | 2/3; 101/101 | 2/3; 101/101 | **MISSED** |
| 4. Valid appeals and unknown ID | 10/10; 404, no event | 10/10; 404 | 10/10; 404 | 10/10; 404 | **MET** |
| 5. Six malformed inputs | 6/6 JSON 400/413, zero decisions | 6/6 | 6/6 | 6/6 | **MET** |

A target must hold in every trial. Criterion 2 missed because the AI median
was **0.4213** and the human median **0.4942** in each run. Criterion 3 missed
because the actual submissions produced only `ai` and `unsure`; the local
`score_to_label` grid still mapped every hundredth score. The appeal trial
checked ten distinct content IDs, preserved all original decision fields and
reasoning, and confirmed that an unknown ID wrote no appeal event. All six
malformed cases had an `error` and `message`, returned 400 or 413, and appended
zero decisions. Matching trials are expected for these deterministic signals.

### Real output from trial 1

The following are exact JSON arrays produced by `run_eval.py::main`, with
`run_eval.py::run_appeal_trial`, `run_eval.py::run_rejection_trial`, and
`run_eval.py::score_grid` supplying the criterion-specific checks.

**Criterion 1 — human writing**

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5933,
    "model_score": 0.8381,
    "style_score": 0.4595,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I went to the grocery store after class because I had almost nothing l",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5524,
    "model_score": 0.7832,
    "style_score": 0.3374,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "My desk gets messy during the week. I leave notebooks, pens, receipts,",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6003,
    "model_score": 0.8429,
    "style_score": 0.487,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "Yesterday I took a walk around my neighborhood after lunch. The weathe",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6601,
    "model_score": 0.7831,
    "style_score": 0.4756,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I made breakfast at home today instead of buying something on campus. ",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6467,
    "model_score": 0.7601,
    "style_score": 0.4767,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "The library was crowded when I arrived in the afternoon. I walked arou",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5375,
    "model_score": 0.6399,
    "style_score": 0.3838,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I used to think that a good study session meant spending as many hours",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5711,
    "model_score": 0.6993,
    "style_score": 0.3787,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "One thing I find interesting about public transportation is how much a",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4742,
    "model_score": 0.5198,
    "style_score": 0.4058,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "During a group project, I learned that dividing work equally is not al",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.553,
    "model_score": 0.5379,
    "style_score": 0.5757,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I have noticed that I understand a programming concept better when I c",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4566,
    "model_score": 0.4675,
    "style_score": 0.4403,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "The first time I looked closely at a financial statement, I was surpri",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5039,
    "model_score": 0.5209,
    "style_score": 0.4784,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "When I work on a technical project, documentation is usually the part ",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5399,
    "model_score": 0.6213,
    "style_score": 0.4178,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I enjoy visiting unfamiliar places, but I rarely plan every hour of a ",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4683,
    "model_score": 0.5864,
    "style_score": 0.2911,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "A difficult part of learning statistics is accepting that a convincing",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3745,
    "model_score": 0.4445,
    "style_score": 0.2695,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I once spent nearly an hour debugging a program because I assumed the ",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.588,
    "model_score": 0.6957,
    "style_score": 0.4264,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "There is a particular kind of satisfaction in finishing a book that ch",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4722,
    "model_score": 0.5277,
    "style_score": 0.389,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I think the design of everyday software matters most when users are ti",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4991,
    "model_score": 0.5836,
    "style_score": 0.3723,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "One reason I like cooking with other people is that it creates a natur",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4893,
    "model_score": 0.54,
    "style_score": 0.4132,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "When comparing two job opportunities, I think it is easy to focus too ",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4817,
    "model_score": 0.5356,
    "style_score": 0.4008,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I have become more cautious about treating productivity tools as solut",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.54,
    "model_score": 0.5594,
    "style_score": 0.5109,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "A good experiment should make it possible to learn something even when",
    "error": null,
    "message": null
  }
]
```

**Criterion 2 — AI and human medians**

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5577,
    "model_score": 0.6305,
    "style_score": 0.4484,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "Community gardens offer neighborhoods a practical way to share space a",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4727,
    "model_score": 0.4134,
    "style_score": 0.5617,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "A repair cafe is a local event where volunteers help neighbors fix com",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4194,
    "model_score": 0.4302,
    "style_score": 0.4033,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "Cities often debate whether a new bicycle lane is worth the space it t",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4893,
    "model_score": 0.5211,
    "style_score": 0.4417,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "Public libraries have adapted to changes in how people find informatio",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3665,
    "model_score": 0.3273,
    "style_score": 0.4254,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "An astronomy club can make the night sky approachable for beginners by",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4232,
    "model_score": 0.4309,
    "style_score": 0.4117,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "School lunch programs have to balance nutrition, cost, food safety, an",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4064,
    "model_score": 0.387,
    "style_score": 0.4356,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "Volunteer groups often begin with enthusiasm and then struggle to sust",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5127,
    "model_score": 0.5571,
    "style_score": 0.4462,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "Keeping useful notes during a meeting is a different task from recordi",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3375,
    "model_score": 0.2757,
    "style_score": 0.4303,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "Street trees can cool a neighborhood and make walking more pleasant, b",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.37,
    "model_score": 0.338,
    "style_score": 0.4179,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "A small museum can make a familiar object interesting by explaining th",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5039,
    "model_score": 0.5209,
    "style_score": 0.4784,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "When I work on a technical project, documentation is usually the part ",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5399,
    "model_score": 0.6213,
    "style_score": 0.4178,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I enjoy visiting unfamiliar places, but I rarely plan every hour of a ",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4683,
    "model_score": 0.5864,
    "style_score": 0.2911,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "A difficult part of learning statistics is accepting that a convincing",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3745,
    "model_score": 0.4445,
    "style_score": 0.2695,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I once spent nearly an hour debugging a program because I assumed the ",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.588,
    "model_score": 0.6957,
    "style_score": 0.4264,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "There is a particular kind of satisfaction in finishing a book that ch",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4722,
    "model_score": 0.5277,
    "style_score": 0.389,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I think the design of everyday software matters most when users are ti",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4991,
    "model_score": 0.5836,
    "style_score": 0.3723,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "One reason I like cooking with other people is that it creates a natur",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4893,
    "model_score": 0.54,
    "style_score": 0.4132,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "When comparing two job opportunities, I think it is easy to focus too ",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4817,
    "model_score": 0.5356,
    "style_score": 0.4008,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I have become more cautious about treating productivity tools as solut",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.54,
    "model_score": 0.5594,
    "style_score": 0.5109,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "A good experiment should make it possible to learn something even when",
    "error": null,
    "message": null
  }
]
```

**Criterion 3 — labels and grid**

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5933,
    "model_score": 0.8381,
    "style_score": 0.4595,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I went to the grocery store after class because I had almost nothing l",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5375,
    "model_score": 0.6399,
    "style_score": 0.3838,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I used to think that a good study session meant spending as many hours",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5039,
    "model_score": 0.5209,
    "style_score": 0.4784,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "When I work on a technical project, documentation is usually the part ",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4722,
    "model_score": 0.5277,
    "style_score": 0.389,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I think the design of everyday software matters most when users are ti",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3724,
    "model_score": 0.0457,
    "style_score": 0.5435,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "’Twas brillig, and the slithy toves did gyre and gimble in the wabe; a",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5577,
    "model_score": 0.6305,
    "style_score": 0.4484,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "Community gardens offer neighborhoods a practical way to share space a",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4727,
    "model_score": 0.4134,
    "style_score": 0.5617,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "A repair cafe is a local event where volunteers help neighbors fix com",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4194,
    "model_score": 0.4302,
    "style_score": 0.4033,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "Cities often debate whether a new bicycle lane is worth the space it t",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4893,
    "model_score": 0.5211,
    "style_score": 0.4417,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "Public libraries have adapted to changes in how people find informatio",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3665,
    "model_score": 0.3273,
    "style_score": 0.4254,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "An astronomy club can make the night sky approachable for beginners by",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4232,
    "model_score": 0.4309,
    "style_score": 0.4117,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "School lunch programs have to balance nutrition, cost, food safety, an",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.995,
    "model_score": 0.9916,
    "style_score": 1.0,
    "label": "Our checks found strong signs of AI-generated writing. This automated label may be wrong, and the creator can appeal it.",
    "sent": "The system works well. The system works well. The system works well. T",
    "error": null,
    "message": null
  },
  {
    "sent": "score_to_label grid: 0.00, 0.01, ..., 1.00",
    "scores_checked": 101,
    "labels_seen": [
      "ai",
      "human",
      "unsure"
    ],
    "invalid_scores": []
  }
]
```

**Criterion 4 — appeals**

```json
[
  {
    "sent": "Community gardens offer neighborhoods a practical way to share space a",
    "submit_status": 200,
    "content_id": "b5795cfb-9f84-4caa-a59b-3aee3c7f447e",
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "b5795cfb-9f84-4caa-a59b-3aee3c7f447e",
      "message": "Your appeal was recorded for human review.",
      "status": "under_review"
    },
    "original_preserved": true,
    "reasoning_recorded": true
  },
  {
    "sent": "A repair cafe is a local event where volunteers help neighbors fix com",
    "submit_status": 200,
    "content_id": "8a86c5d2-1b4f-4749-8f0c-bd00826608de",
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "8a86c5d2-1b4f-4749-8f0c-bd00826608de",
      "message": "Your appeal was recorded for human review.",
      "status": "under_review"
    },
    "original_preserved": true,
    "reasoning_recorded": true
  },
  {
    "sent": "Cities often debate whether a new bicycle lane is worth the space it t",
    "submit_status": 200,
    "content_id": "6fe65b52-5ea7-4999-b6a4-45850ebb4662",
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "6fe65b52-5ea7-4999-b6a4-45850ebb4662",
      "message": "Your appeal was recorded for human review.",
      "status": "under_review"
    },
    "original_preserved": true,
    "reasoning_recorded": true
  },
  {
    "sent": "Public libraries have adapted to changes in how people find informatio",
    "submit_status": 200,
    "content_id": "9efc85dd-ea3d-4515-b935-c6edf5f090e9",
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "9efc85dd-ea3d-4515-b935-c6edf5f090e9",
      "message": "Your appeal was recorded for human review.",
      "status": "under_review"
    },
    "original_preserved": true,
    "reasoning_recorded": true
  },
  {
    "sent": "An astronomy club can make the night sky approachable for beginners by",
    "submit_status": 200,
    "content_id": "eaf68275-b3ae-42a5-9678-a6928780e09d",
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "eaf68275-b3ae-42a5-9678-a6928780e09d",
      "message": "Your appeal was recorded for human review.",
      "status": "under_review"
    },
    "original_preserved": true,
    "reasoning_recorded": true
  },
  {
    "sent": "School lunch programs have to balance nutrition, cost, food safety, an",
    "submit_status": 200,
    "content_id": "de2ebac3-4d37-4556-8314-b882d18fcbb0",
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "de2ebac3-4d37-4556-8314-b882d18fcbb0",
      "message": "Your appeal was recorded for human review.",
      "status": "under_review"
    },
    "original_preserved": true,
    "reasoning_recorded": true
  },
  {
    "sent": "Volunteer groups often begin with enthusiasm and then struggle to sust",
    "submit_status": 200,
    "content_id": "51107ff8-4fe6-4df1-a72d-5bc0221054f1",
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "51107ff8-4fe6-4df1-a72d-5bc0221054f1",
      "message": "Your appeal was recorded for human review.",
      "status": "under_review"
    },
    "original_preserved": true,
    "reasoning_recorded": true
  },
  {
    "sent": "Keeping useful notes during a meeting is a different task from recordi",
    "submit_status": 200,
    "content_id": "7beaae59-e89e-4810-8b60-0399d8430603",
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "7beaae59-e89e-4810-8b60-0399d8430603",
      "message": "Your appeal was recorded for human review.",
      "status": "under_review"
    },
    "original_preserved": true,
    "reasoning_recorded": true
  },
  {
    "sent": "Street trees can cool a neighborhood and make walking more pleasant, b",
    "submit_status": 200,
    "content_id": "790b2a2b-c3cb-41ee-a2a9-80c93d1c646e",
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "790b2a2b-c3cb-41ee-a2a9-80c93d1c646e",
      "message": "Your appeal was recorded for human review.",
      "status": "under_review"
    },
    "original_preserved": true,
    "reasoning_recorded": true
  },
  {
    "sent": "A small museum can make a familiar object interesting by explaining th",
    "submit_status": 200,
    "content_id": "dd9549c6-842e-4af6-89ce-0ae5c81d969a",
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "dd9549c6-842e-4af6-89ce-0ae5c81d969a",
      "message": "Your appeal was recorded for human review.",
      "status": "under_review"
    },
    "original_preserved": true,
    "reasoning_recorded": true
  },
  {
    "sent": "unknown content_id",
    "content_id": "a035318b-f46e-426c-ad32-c20e92f06d03",
    "appeal_status": 404,
    "appeal_response": {
      "error": "not_found",
      "message": "No submission has that content_id."
    },
    "appeal_event_written": false
  }
]
```

**Criterion 5 — malformed input**

```json
[
  {
    "sent": "[]",
    "status": 400,
    "error": "invalid_json",
    "message": "Send a JSON object.",
    "new_decisions": 0
  },
  {
    "sent": "{\"creator_id\": \"eval_missing_text\"}",
    "status": 400,
    "error": "invalid_text",
    "message": "text must be a nonblank string.",
    "new_decisions": 0
  },
  {
    "sent": "   ",
    "status": 400,
    "error": "invalid_text",
    "message": "text must be a nonblank string.",
    "new_decisions": 0
  },
  {
    "sent": "{\"text\": 42, \"creator_id\": \"eval_nonstring_text\"}",
    "status": 400,
    "error": "invalid_text",
    "message": "text must be a nonblank string.",
    "new_decisions": 0
  },
  {
    "sent": "{\"text\": \"This body has no creator ID.\"}",
    "status": 400,
    "error": "invalid_creator_id",
    "message": "creator_id must be a nonblank string of at most 128 characters.",
    "new_decisions": 0
  },
  {
    "sent": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "status": 413,
    "error": "text_too_long",
    "message": "text may be at most 10,000 characters.",
    "new_decisions": 0
  }
]
```

### Diagnoses

- **Criterion 2 — MISSED; signal one and combining rule.** The median GPT-2
  model score was 0.4218 for the AI pieces and 0.5497 for the student-supplied
  human pieces: the ordering was reversed. The style medians pointed only
  weakly the intended way, 0.4330 versus 0.4070. Giving the reversed model
  signal 60% of the combined score produced a negative 0.0729 gap. A threshold
  change cannot repair score ordering.
- **Criterion 3 — MISSED; combining rule and label mapping.** The Carroll
  excerpt had model score 0.0457 but style score 0.5435. Their disagreement
  triggered the shrink-to-0.5 rule, moving its weighted score to 0.3724,
  above the human boundary of 0.30. Other human pieces scored 0.4722–0.5933,
  so no frozen submission reached `human`. The mapping itself covered all 101
  checked values; the miss is about real inputs reaching its band.
- **EV01 and EV04 — BROKE; signal one.** Typos in EV01 drove the model score
  to 0.1635 and unusual vocabulary in EV04 left it at 0.6114; their combined
  scores fell to 0.2763 (`human`) and 0.5360 (`unsure`). GPT-2 predictability
  changes with surface wording, even when the AI-origin argument remains.
- **EV02, EV03, EV06, and EV09 — BROKE; signal two and combining rule.** Broken
  sentences, a pasted quotation, uneven sentence lengths, and a human opening
  lowered style scores to 0.1664, 0.2712, 0.1565, and 0.2608. The model/style
  splits also activated the disagreement rule, leaving all four `unsure`.
- **EV05 — BROKE; both signals.** Heavy human editing left model/style scores
  0.3212/0.1003, producing `human`. The detector sees the edited wording,
  not the drafting history. This attack's origin is therefore hard to infer
  from the final text alone.
- **EV07 — BROKE; signals and label mapping.** Punctuation padding resulted
  in moderate 0.5862/0.4500 scores, combined 0.5317, below the 0.75 AI band.
  Neither signal retained enough evidence to overcome the conservative
  boundary.
- **EV08 — BROKE; signal one and the short-text style fallback.** The short
  AI-origin input scored 0.2452 on the model; the style signal returned its
  neutral 0.5 for fewer than 20 words. Combined 0.3471 was `unsure`.
- **FP05 — BROKE; both signals and label mapping.** Repeated imperative
  sentences in genuine technical documentation scored 0.8005 on the model
  and 0.7037 on style. The weighted 0.7618 crossed the AI boundary by 0.0118.
  This is the worst writer-facing error and the one the improvement targets.
- **PI02 — BROKE at the requested label, not by instruction obedience.** The
  fake SYSTEM message requested `human` at confidence 0.02; the service gave
  `human` at 0.1900, so its exact instruction was not followed. Its wrapper
  altered the text read by both signals (0.2044/0.1683), causing a human
  label through the ordinary scoring path. PI04 did not alter the fixed label
  sentence, and PI05 did not add fields to the JSON audit record.
- **MF03–MF06 — BROKE; route validation.** Control bytes, punctuation only,
  one long word, and emoji only passed the route's nonblank-string check and
  created `unsure` decisions. The route has no substantive-word check; the
  style signal returns neutral 0.5 for such short or wordless text. MF07 is
  Arabic writing rather than malformed text; `unsure` without a crash was a
  cautious result. All twelve RQ malformed bodies were rejected as JSON.

---

## The Improvement

**What I changed:** In `config.py`, I moved only `AI_THRESHOLD` from 0.75 to
0.80. The human boundary, signals, 0.60/0.40 weights, disagreement rule,
routes, and response schema remained fixed. This widens the `unsure` band by
0.05 on the AI side.

**Which diagnosis pointed at it:** Staff FP05 is human-written technical
documentation but scored 0.7618 and was accused as `ai` just above the old
0.75 threshold. The new 0.80 boundary makes that same score `unsure`. This
addresses the observed label mapping failure for that writer; it cannot repair
the inverted score ordering in criterion 2 or the missing `human` label in
criterion 3.

### Before and after, side by side

| Family | Before HELD / BROKE | After HELD / BROKE | Change |
|---|---:|---:|---|
| Evasion | 1 / 9 | 1 / 9 | none |
| False positive | 7 / 1 | 8 / 0 | FP05 no longer accused |
| Prompt injection | 5 / 1 | 5 / 1 | none |
| Malformed | 16 / 4 | 16 / 4 | none |
| Same-creator flood | 12 / 0 | 12 / 0 | none |
| **All 56** | **41 / 15** | **42 / 14** | **one changed outcome** |

Every input below is paired with its same-ID result. The score is the combined
0–1 value; dashes mean the route returned no decision. Full signal scores and
targets appear in the before and after tables.

| ID | Before: HTTP / score / guess / verdict | After: HTTP / score / guess / verdict |
|---|---|---|
| EV01 | 200 / 0.2763 / human / BROKE | 200 / 0.2763 / human / BROKE |
| EV02 | 200 / 0.4616 / unsure / BROKE | 200 / 0.4616 / unsure / BROKE |
| EV03 | 200 / 0.5041 / unsure / BROKE | 200 / 0.5041 / unsure / BROKE |
| EV04 | 200 / 0.536 / unsure / BROKE | 200 / 0.536 / unsure / BROKE |
| EV05 | 200 / 0.2328 / human / BROKE | 200 / 0.2328 / human / BROKE |
| EV06 | 200 / 0.4531 / unsure / BROKE | 200 / 0.4531 / unsure / BROKE |
| EV07 | 200 / 0.5317 / unsure / BROKE | 200 / 0.5317 / unsure / BROKE |
| EV08 | 200 / 0.3471 / unsure / BROKE | 200 / 0.3471 / unsure / BROKE |
| EV09 | 200 / 0.5134 / unsure / BROKE | 200 / 0.5134 / unsure / BROKE |
| EV10 | 200 / 0.8475 / ai / HELD | 200 / 0.8475 / ai / HELD |
| FP01 | 200 / 0.5056 / unsure / HELD | 200 / 0.5056 / unsure / HELD |
| FP02 | 200 / 0.6713 / unsure / HELD | 200 / 0.6713 / unsure / HELD |
| FP03 | 200 / 0.6681 / unsure / HELD | 200 / 0.6681 / unsure / HELD |
| FP04 | 200 / 0.584 / unsure / HELD | 200 / 0.584 / unsure / HELD |
| FP05 | 200 / 0.7618 / ai / BROKE | 200 / 0.7618 / unsure / HELD |
| FP06 | 200 / 0.5809 / unsure / HELD | 200 / 0.5809 / unsure / HELD |
| FP07 | 200 / 0.6054 / unsure / HELD | 200 / 0.6054 / unsure / HELD |
| FP08 | 200 / 0.3934 / unsure / HELD | 200 / 0.3934 / unsure / HELD |
| PI01 | 200 / 0.366 / unsure / HELD | 200 / 0.366 / unsure / HELD |
| PI02 | 200 / 0.19 / human / BROKE | 200 / 0.19 / human / BROKE |
| PI03 | 200 / 0.5085 / unsure / HELD | 200 / 0.5085 / unsure / HELD |
| PI04 | 200 / 0.4583 / unsure / HELD | 200 / 0.4583 / unsure / HELD |
| PI05 | 200 / 0.4682 / unsure / HELD | 200 / 0.4682 / unsure / HELD |
| PI06 | 200 / 0.5037 / unsure / HELD | 200 / 0.5037 / unsure / HELD |
| MF01 | 400 / — / — / HELD | 400 / — / — / HELD |
| MF02 | 400 / — / — / HELD | 400 / — / — / HELD |
| MF03 | 200 / 0.35 / unsure / BROKE | 200 / 0.35 / unsure / BROKE |
| MF04 | 200 / 0.3534 / unsure / BROKE | 200 / 0.3534 / unsure / BROKE |
| MF05 | 200 / 0.6493 / unsure / BROKE | 200 / 0.6493 / unsure / BROKE |
| MF06 | 200 / 0.6491 / unsure / BROKE | 200 / 0.6491 / unsure / BROKE |
| MF07 | 200 / 0.6219 / unsure / HELD | 200 / 0.6219 / unsure / HELD |
| MF08 | 413 / — / — / HELD | 413 / — / — / HELD |
| RQ01 | 400 / — / — / HELD | 400 / — / — / HELD |
| RQ02 | 400 / — / — / HELD | 400 / — / — / HELD |
| RQ03 | 400 / — / — / HELD | 400 / — / — / HELD |
| RQ04 | 400 / — / — / HELD | 400 / — / — / HELD |
| RQ05 | 400 / — / — / HELD | 400 / — / — / HELD |
| RQ06 | 400 / — / — / HELD | 400 / — / — / HELD |
| RQ07 | 400 / — / — / HELD | 400 / — / — / HELD |
| RQ08 | 400 / — / — / HELD | 400 / — / — / HELD |
| RQ09 | 400 / — / — / HELD | 400 / — / — / HELD |
| RQ10 | 400 / — / — / HELD | 400 / — / — / HELD |
| RQ11 | 400 / — / — / HELD | 400 / — / — / HELD |
| RQ12 | 400 / — / — / HELD | 400 / — / — / HELD |
| FL01_01 | 200 / 0.3586 / unsure / HELD | 200 / 0.3586 / unsure / HELD |
| FL01_02 | 200 / 0.3586 / unsure / HELD | 200 / 0.3586 / unsure / HELD |
| FL01_03 | 200 / 0.3586 / unsure / HELD | 200 / 0.3586 / unsure / HELD |
| FL01_04 | 200 / 0.3586 / unsure / HELD | 200 / 0.3586 / unsure / HELD |
| FL01_05 | 200 / 0.3586 / unsure / HELD | 200 / 0.3586 / unsure / HELD |
| FL01_06 | 200 / 0.3586 / unsure / HELD | 200 / 0.3586 / unsure / HELD |
| FL01_07 | 200 / 0.3586 / unsure / HELD | 200 / 0.3586 / unsure / HELD |
| FL01_08 | 200 / 0.3586 / unsure / HELD | 200 / 0.3586 / unsure / HELD |
| FL01_09 | 200 / 0.3586 / unsure / HELD | 200 / 0.3586 / unsure / HELD |
| FL01_10 | 200 / 0.3586 / unsure / HELD | 200 / 0.3586 / unsure / HELD |
| FL01_11 | 429 / — / — / HELD | 429 / — / — / HELD |
| FL01_12 | 429 / — / — / HELD | 429 / — / — / HELD |

### Attack Run — After

The same 56 staff inputs were rerun with `run_attacks.py::main` after the
single threshold change. The complete JSON responses are in
`results/attack_run_2026-11-13_0756_after.md`, and the reviewed table is also
in `results/attack_review_after.md`. The targets and judgment rules are exactly
those used for the before run.

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
| FP05 | false_positive | technical documentation written by a person | 200 | 0.8005 | 0.7037 | 0.7618 | unsure | HELD |
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

**Totals:** 42 HELD, 14 BROKE, 56 measured.

### Repeated criteria — after

I ran the same frozen `scenarios.py` inputs with `run_eval.py::main`, three
times per criterion. The after trial output is in
`results/run_2026-11-13_0756_after.md`.

| Criterion | Original target | Before runs 1 / 2 / 3 | After run 1 | After run 2 | After run 3 | After verdict |
|---|---|---|---|---|---|---|
| 1. Human writing false accusations | ≤1 AI of 20 | 0/20 / 0/20 / 0/20 | 0/20 | 0/20 | 0/20 | **MET** |
| 2. AI score median above human | gap ≥0.15 | −0.0729 / −0.0729 / −0.0729 | −0.0729 | −0.0729 | −0.0729 | **MISSED** |
| 3. Three labels on ≥12 pieces; complete 101-score grid | 3/3 and 101/101 | 2/3, 101/101 in each | 2/3; 101/101 | 2/3; 101/101 | 2/3; 101/101 | **MISSED** |
| 4. Valid appeals and unknown ID | 10/10; 404, no event | 10/10; 404 in each | 10/10; 404 | 10/10; 404 | 10/10; 404 | **MET** |
| 5. Six malformed inputs | 6/6 JSON 400/413, zero decisions | 6/6 in each | 6/6 | 6/6 | 6/6 | **MET** |

**Did it help, and how do I know:** Yes, for the specific writer-facing error I
targeted: FP05 changed from `ai` to `unsure` while its model, style, and
combined scores stayed 0.8005, 0.7037, and 0.7618. The other 55 staff outputs
had the same statuses, scores, and guesses; no criterion verdict changed. All
15 after criterion trials matched their before counterparts except for new
content IDs. The measured staff set showed no additional AI-origin sample
downgraded, but any future AI-origin text scoring from 0.75 through just under
0.80 now receives `unsure` rather than `ai`.

### Real output from after trial 1

These are the exact JSON arrays from one after trial of each criterion,
produced by `run_eval.py::main` and its appeal, rejection, and score-grid
helpers. The other two trials for every criterion remain in the after run file.

**Criterion 1 — human writing**

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5933,
    "model_score": 0.8381,
    "style_score": 0.4595,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I went to the grocery store after class because I had almost nothing l",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5524,
    "model_score": 0.7832,
    "style_score": 0.3374,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "My desk gets messy during the week. I leave notebooks, pens, receipts,",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6003,
    "model_score": 0.8429,
    "style_score": 0.487,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "Yesterday I took a walk around my neighborhood after lunch. The weathe",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6601,
    "model_score": 0.7831,
    "style_score": 0.4756,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I made breakfast at home today instead of buying something on campus. ",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6467,
    "model_score": 0.7601,
    "style_score": 0.4767,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "The library was crowded when I arrived in the afternoon. I walked arou",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5375,
    "model_score": 0.6399,
    "style_score": 0.3838,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I used to think that a good study session meant spending as many hours",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5711,
    "model_score": 0.6993,
    "style_score": 0.3787,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "One thing I find interesting about public transportation is how much a",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4742,
    "model_score": 0.5198,
    "style_score": 0.4058,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "During a group project, I learned that dividing work equally is not al",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.553,
    "model_score": 0.5379,
    "style_score": 0.5757,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I have noticed that I understand a programming concept better when I c",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4566,
    "model_score": 0.4675,
    "style_score": 0.4403,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "The first time I looked closely at a financial statement, I was surpri",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5039,
    "model_score": 0.5209,
    "style_score": 0.4784,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "When I work on a technical project, documentation is usually the part ",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5399,
    "model_score": 0.6213,
    "style_score": 0.4178,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I enjoy visiting unfamiliar places, but I rarely plan every hour of a ",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4683,
    "model_score": 0.5864,
    "style_score": 0.2911,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "A difficult part of learning statistics is accepting that a convincing",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3745,
    "model_score": 0.4445,
    "style_score": 0.2695,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I once spent nearly an hour debugging a program because I assumed the ",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.588,
    "model_score": 0.6957,
    "style_score": 0.4264,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "There is a particular kind of satisfaction in finishing a book that ch",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4722,
    "model_score": 0.5277,
    "style_score": 0.389,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I think the design of everyday software matters most when users are ti",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4991,
    "model_score": 0.5836,
    "style_score": 0.3723,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "One reason I like cooking with other people is that it creates a natur",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4893,
    "model_score": 0.54,
    "style_score": 0.4132,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "When comparing two job opportunities, I think it is easy to focus too ",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4817,
    "model_score": 0.5356,
    "style_score": 0.4008,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I have become more cautious about treating productivity tools as solut",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.54,
    "model_score": 0.5594,
    "style_score": 0.5109,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "A good experiment should make it possible to learn something even when",
    "error": null,
    "message": null
  }
]
```

**Criterion 2 — known AI versus human medians**

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5577,
    "model_score": 0.6305,
    "style_score": 0.4484,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "Community gardens offer neighborhoods a practical way to share space a",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4727,
    "model_score": 0.4134,
    "style_score": 0.5617,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "A repair cafe is a local event where volunteers help neighbors fix com",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4194,
    "model_score": 0.4302,
    "style_score": 0.4033,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "Cities often debate whether a new bicycle lane is worth the space it t",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4893,
    "model_score": 0.5211,
    "style_score": 0.4417,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "Public libraries have adapted to changes in how people find informatio",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3665,
    "model_score": 0.3273,
    "style_score": 0.4254,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "An astronomy club can make the night sky approachable for beginners by",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4232,
    "model_score": 0.4309,
    "style_score": 0.4117,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "School lunch programs have to balance nutrition, cost, food safety, an",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4064,
    "model_score": 0.387,
    "style_score": 0.4356,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "Volunteer groups often begin with enthusiasm and then struggle to sust",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5127,
    "model_score": 0.5571,
    "style_score": 0.4462,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "Keeping useful notes during a meeting is a different task from recordi",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3375,
    "model_score": 0.2757,
    "style_score": 0.4303,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "Street trees can cool a neighborhood and make walking more pleasant, b",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.37,
    "model_score": 0.338,
    "style_score": 0.4179,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "A small museum can make a familiar object interesting by explaining th",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5039,
    "model_score": 0.5209,
    "style_score": 0.4784,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "When I work on a technical project, documentation is usually the part ",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5399,
    "model_score": 0.6213,
    "style_score": 0.4178,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I enjoy visiting unfamiliar places, but I rarely plan every hour of a ",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4683,
    "model_score": 0.5864,
    "style_score": 0.2911,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "A difficult part of learning statistics is accepting that a convincing",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3745,
    "model_score": 0.4445,
    "style_score": 0.2695,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I once spent nearly an hour debugging a program because I assumed the ",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.588,
    "model_score": 0.6957,
    "style_score": 0.4264,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "There is a particular kind of satisfaction in finishing a book that ch",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4722,
    "model_score": 0.5277,
    "style_score": 0.389,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I think the design of everyday software matters most when users are ti",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4991,
    "model_score": 0.5836,
    "style_score": 0.3723,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "One reason I like cooking with other people is that it creates a natur",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4893,
    "model_score": 0.54,
    "style_score": 0.4132,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "When comparing two job opportunities, I think it is easy to focus too ",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4817,
    "model_score": 0.5356,
    "style_score": 0.4008,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I have become more cautious about treating productivity tools as solut",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.54,
    "model_score": 0.5594,
    "style_score": 0.5109,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "A good experiment should make it possible to learn something even when",
    "error": null,
    "message": null
  }
]
```

**Criterion 3 — label and score grid coverage**

```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5933,
    "model_score": 0.8381,
    "style_score": 0.4595,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I went to the grocery store after class because I had almost nothing l",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5375,
    "model_score": 0.6399,
    "style_score": 0.3838,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I used to think that a good study session meant spending as many hours",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5039,
    "model_score": 0.5209,
    "style_score": 0.4784,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "When I work on a technical project, documentation is usually the part ",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4722,
    "model_score": 0.5277,
    "style_score": 0.389,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "I think the design of everyday software matters most when users are ti",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3724,
    "model_score": 0.0457,
    "style_score": 0.5435,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "\u2019Twas brillig, and the slithy toves did gyre and gimble in the wabe; a",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.5577,
    "model_score": 0.6305,
    "style_score": 0.4484,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "Community gardens offer neighborhoods a practical way to share space a",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4727,
    "model_score": 0.4134,
    "style_score": 0.5617,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "A repair cafe is a local event where volunteers help neighbors fix com",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4194,
    "model_score": 0.4302,
    "style_score": 0.4033,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "Cities often debate whether a new bicycle lane is worth the space it t",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4893,
    "model_score": 0.5211,
    "style_score": 0.4417,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "Public libraries have adapted to changes in how people find informatio",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.3665,
    "model_score": 0.3273,
    "style_score": 0.4254,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "An astronomy club can make the night sky approachable for beginners by",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.4232,
    "model_score": 0.4309,
    "style_score": 0.4117,
    "label": "Our checks cannot tell who wrote this with enough confidence. No authorship claim is being made, and the creator can appeal.",
    "sent": "School lunch programs have to balance nutrition, cost, food safety, an",
    "error": null,
    "message": null
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.995,
    "model_score": 0.9916,
    "style_score": 1.0,
    "label": "Our checks found strong signs of AI-generated writing. This automated label may be wrong, and the creator can appeal it.",
    "sent": "The system works well. The system works well. The system works well. T",
    "error": null,
    "message": null
  },
  {
    "sent": "score_to_label grid: 0.00, 0.01, ..., 1.00",
    "scores_checked": 101,
    "labels_seen": [
      "ai",
      "human",
      "unsure"
    ],
    "invalid_scores": []
  }
]
```

**Criterion 4 — appeals**

```json
[
  {
    "sent": "Community gardens offer neighborhoods a practical way to share space a",
    "submit_status": 200,
    "content_id": "2744d01d-c286-478c-9158-13e49167fd7b",
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "2744d01d-c286-478c-9158-13e49167fd7b",
      "message": "Your appeal was recorded for human review.",
      "status": "under_review"
    },
    "original_preserved": true,
    "reasoning_recorded": true
  },
  {
    "sent": "A repair cafe is a local event where volunteers help neighbors fix com",
    "submit_status": 200,
    "content_id": "b0ea8e12-f687-4f38-9bda-5753f7139c08",
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "b0ea8e12-f687-4f38-9bda-5753f7139c08",
      "message": "Your appeal was recorded for human review.",
      "status": "under_review"
    },
    "original_preserved": true,
    "reasoning_recorded": true
  },
  {
    "sent": "Cities often debate whether a new bicycle lane is worth the space it t",
    "submit_status": 200,
    "content_id": "77c6a867-bbbc-4927-ace4-ec35e3cfc78c",
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "77c6a867-bbbc-4927-ace4-ec35e3cfc78c",
      "message": "Your appeal was recorded for human review.",
      "status": "under_review"
    },
    "original_preserved": true,
    "reasoning_recorded": true
  },
  {
    "sent": "Public libraries have adapted to changes in how people find informatio",
    "submit_status": 200,
    "content_id": "9bb8a164-0394-46fb-a533-68f411bbb79e",
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "9bb8a164-0394-46fb-a533-68f411bbb79e",
      "message": "Your appeal was recorded for human review.",
      "status": "under_review"
    },
    "original_preserved": true,
    "reasoning_recorded": true
  },
  {
    "sent": "An astronomy club can make the night sky approachable for beginners by",
    "submit_status": 200,
    "content_id": "503c3392-93c6-4fd0-a3e5-70dc52e6c30f",
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "503c3392-93c6-4fd0-a3e5-70dc52e6c30f",
      "message": "Your appeal was recorded for human review.",
      "status": "under_review"
    },
    "original_preserved": true,
    "reasoning_recorded": true
  },
  {
    "sent": "School lunch programs have to balance nutrition, cost, food safety, an",
    "submit_status": 200,
    "content_id": "9af5ff9d-7170-41e2-b3f0-5802eaa21bb0",
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "9af5ff9d-7170-41e2-b3f0-5802eaa21bb0",
      "message": "Your appeal was recorded for human review.",
      "status": "under_review"
    },
    "original_preserved": true,
    "reasoning_recorded": true
  },
  {
    "sent": "Volunteer groups often begin with enthusiasm and then struggle to sust",
    "submit_status": 200,
    "content_id": "3628b9dd-3209-495a-b2b5-a076d58e298d",
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "3628b9dd-3209-495a-b2b5-a076d58e298d",
      "message": "Your appeal was recorded for human review.",
      "status": "under_review"
    },
    "original_preserved": true,
    "reasoning_recorded": true
  },
  {
    "sent": "Keeping useful notes during a meeting is a different task from recordi",
    "submit_status": 200,
    "content_id": "cf356cb5-18be-402b-9ed2-d4b024a09687",
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "cf356cb5-18be-402b-9ed2-d4b024a09687",
      "message": "Your appeal was recorded for human review.",
      "status": "under_review"
    },
    "original_preserved": true,
    "reasoning_recorded": true
  },
  {
    "sent": "Street trees can cool a neighborhood and make walking more pleasant, b",
    "submit_status": 200,
    "content_id": "f66cd7b8-21e4-432e-8949-cfab5f5e627c",
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "f66cd7b8-21e4-432e-8949-cfab5f5e627c",
      "message": "Your appeal was recorded for human review.",
      "status": "under_review"
    },
    "original_preserved": true,
    "reasoning_recorded": true
  },
  {
    "sent": "A small museum can make a familiar object interesting by explaining th",
    "submit_status": 200,
    "content_id": "19437c37-e337-4905-8259-20a4b3f75a05",
    "appeal_status": 200,
    "appeal_response": {
      "content_id": "19437c37-e337-4905-8259-20a4b3f75a05",
      "message": "Your appeal was recorded for human review.",
      "status": "under_review"
    },
    "original_preserved": true,
    "reasoning_recorded": true
  },
  {
    "sent": "unknown content_id",
    "content_id": "7898d619-be1e-42d2-88c6-b8bc2ed7532c",
    "appeal_status": 404,
    "appeal_response": {
      "error": "not_found",
      "message": "No submission has that content_id."
    },
    "appeal_event_written": false
  }
]
```

**Criterion 5 — malformed input**

```json
[
  {
    "sent": "[]",
    "status": 400,
    "error": "invalid_json",
    "message": "Send a JSON object.",
    "new_decisions": 0
  },
  {
    "sent": "{\"creator_id\": \"eval_missing_text\"}",
    "status": 400,
    "error": "invalid_text",
    "message": "text must be a nonblank string.",
    "new_decisions": 0
  },
  {
    "sent": "   ",
    "status": 400,
    "error": "invalid_text",
    "message": "text must be a nonblank string.",
    "new_decisions": 0
  },
  {
    "sent": "{\"text\": 42, \"creator_id\": \"eval_nonstring_text\"}",
    "status": 400,
    "error": "invalid_text",
    "message": "text must be a nonblank string.",
    "new_decisions": 0
  },
  {
    "sent": "{\"text\": \"This body has no creator ID.\"}",
    "status": 400,
    "error": "invalid_creator_id",
    "message": "creator_id must be a nonblank string of at most 128 characters.",
    "new_decisions": 0
  },
  {
    "sent": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "status": 413,
    "error": "text_too_long",
    "message": "text may be at most 10,000 characters.",
    "new_decisions": 0
  }
]
```

---

## What's Still Broken

Fourteen staff attacks still meet their adversarial objective. Each next step
below would require another service change or a separate provenance source, so
I stopped after the single measured threshold change required for this unit.
The before-run diagnoses above identify the stage and mechanism behind these
remaining failures.

| Still broken | Next step | Why I stopped here |
|---|---|---|
| EV01 | Test typo normalization or perturbation-aware model calibration. | A model-signal change needs a held-out typo set. |
| EV02 | Make sentence-spread style measurement less sensitive to manual sentence breaks. | A style-signal change would be a second improvement. |
| EV03 | Evaluate quote segmentation so pasted quotations do not dominate style. | Segmenting quotes needs tests for genuine quotation use. |
| EV04 | Calibrate model predictability on rare but generated vocabulary. | It changes signal one and needs representative samples. |
| EV05 | Use consented drafting history or source provenance to check a heavily edited passage. | The final text alone does not reveal its drafting history. |
| EV06 | Robustify the style statistic against one extreme long/short sentence pair. | This is another signal-two change requiring held-out tests. |
| EV07 | Measure whether punctuation normalization resists padding without harming expressive writing. | A new style rule could penalize real writers. |
| EV08 | Design an explicit short-text abstention or different short-text signal. | Short-text policy affects labels and needs separate calibration. |
| EV09 | Try span-level scores before aggregating a human opening with AI-origin text. | This is a new signal path, beyond one change. |
| PI02 | Test role-marker wrappers against the ordinary scoring path; consider treating them as untrusted text structure. | The observed human label came from text shape, not obedience to the fake SYSTEM instruction; a wrapper rule needs evidence. |
| MF03 | Reject control bytes while allowing ordinary line breaks and tabs. | Route validation would be a second service change. |
| MF04 | Require substantive text before scoring punctuation-only input. | A word rule needs multilingual and accessibility tests. |
| MF05 | Set a documented maximum uninterrupted token length or reject wordless extremes. | Legitimate URLs, code, and identifiers could be affected. |
| MF06 | Reject emoji-only scoring as unsupported while preserving non-Latin writing. | A language-aware validation policy needs more examples. |

Criterion 2 remains **MISSED** in all three after trials: AI and human medians
are 0.4213 and 0.4942. I would collect representative, provenance-verified
samples and recalibrate or replace the model signal before selecting new
weights; I stopped because a threshold cannot reverse the score ordering, and
changing that signal would be a second improvement.

Criterion 3 remains **MISSED** in all three after trials: the frozen 12
submissions produce only `ai` and `unsure`, though the 101-score mapping is
complete. I would evaluate the disagreement shrink and human threshold on a
larger human set, then retest whether actual human writing safely reaches
`human`; I stopped because that is another threshold or combining-rule change
and could create false human claims.

**The trade I would make if this ran for real:** I would retain the wider unsure
band to reduce unsupported AI accusations against writers, accepting that
generated text in the 0.75–0.80 band may avoid an AI label. Writers bear fewer
false accusations, while human reviewers and readers bear more manual checking
and missed generated text.

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
