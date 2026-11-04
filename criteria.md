# Acceptance criteria — Provenance Guard

These five targets were set before any detector or submission results were
examined. They are **AI-drafted proposals** for the repository owner to review
and adopt or revise before submission. The source brief asks the student to
write and defend their own criteria; this file does not claim otherwise.

For text-based trials, freeze the test pieces and their known provenance
before the first run. Apply the targets independently to each of the three
trials in the next unit, without changing thresholds between trials.

## 1. Limit false accusations of human writing

Of 20 preselected human-written pieces of 80–200 words, including at least
five deliberately plain pieces, **at most one** may receive the
high-confidence AI label in each trial.

**Why this target:** A wrong accusation has a direct cost for the writer. A
5% ceiling is demanding enough to reveal whether ordinary prose is being
mistaken for generated text.

## 2. Separate known AI and human samples

For ten preselected AI-generated pieces and ten preselected human-written
pieces of 80–200 words, the **median combined AI-likelihood score** of the AI
group must exceed the human group's median by **at least 0.15** in each trial.

**Why this target:** A score spread smaller than 0.15 gives the site little
practical reason to use the detector, even if most individual labels say
"unsure." Group medians avoid letting one odd sample decide the result.

## 3. Make all three labels reachable

Across a frozen set of **at least 12** mixed-provenance submissions, each of
`human`, `unsure`, and `ai` must appear **at least once** in each trial.
Separately, `score_to_label` must return one of those three labels for every
score in **0.00, 0.01, ..., 1.00**, with no gap or exception.

**Why this target:** The service promises three reader-facing outcomes. A
label that no real submission can reach is not a working option, while the
grid check catches holes at threshold boundaries.

## 4. Preserve every valid appeal

For **ten** valid, distinct `content_id` values, **ten of ten** appeals must
return `under_review` and append an appeal event containing the submitted
reasoning. Each original decision and its two signal scores must remain in
the audit log unchanged. An unknown id must return **404** and append no
appeal event.

**Why this target:** An appeal is a writer's only way to challenge a false
accusation. Losing even one would undermine the safety of the workflow.

## 5. Reject malformed or oversized submissions predictably

For each of these **six** inputs — no JSON object, missing `text`, blank
`text`, non-string `text`, missing `creator_id`, and text over **10,000
characters** — `POST /submit` must return JSON with an `error` and `message`,
use **400** or **413**, create **zero decision entries**, and never return 500.

**Why this target:** Bad input should be a clear caller error, not an
expensive model call or an unexplained server failure. The size cap also
limits work a single request can impose.
