# Provenance Guard: submission path and contract

This plan was written before scoring any sample submissions. The service is a
local aid for a writing site, not proof of authorship.

## The path from text to a reader's label

1. `POST /submit` parses a JSON object containing `text` and `creator_id`.
2. The route rejects missing, blank, non-string, or oversized fields with a
   clear 4xx response and an audit rejection event.
3. The route assigns a new `content_id` to a valid submission.
4. `detector.model_signal` scores how predictable the words are to a local
   language model. `stylometry.style_signal` measures the shape of the text.
5. `scoring.combine_signals` turns the two 0–1 signals into one AI-likelihood
   score. A large disagreement pulls the result toward uncertainty.
6. `scoring.score_to_label` chooses `human`, `unsure`, or `ai` and a complete
   sentence a reader can understand.
7. `audit.log_decision` records the decision and both input scores; the route
   returns the id, guess, score, and label as JSON.

## The signals and their blind spots

- The model signal measures language-model predictability, using perplexity.
  Generated prose can be very predictable. Plain human writing, including work
  from a younger writer or someone writing in a second language, can be equally
  predictable. It cannot establish who wrote the text.
- The style signal measures sentence-length spread, word variety, and
  punctuation density without reading meaning. Generated prose may be more
  regular. A person can write regularly, and an AI user can add a few unusual
  marks or sentence breaks. It cannot distinguish those cases.

## False-positive path

A real writer using short, ordinary sentences might receive a high model
score. If the style score agrees, the combined score could cross the AI label
threshold and the response would display an automated, explicitly uncertain
accusation. The writer can send the returned `content_id` and their reasoning
to `POST /appeal`. The appeal adds an `under_review` event to the audit log,
preserving the original decision for a person to inspect. Because a false
accusation is costly, the AI threshold is deliberately high and disagreement
pulls the combined score into the unsure band.

## Endpoint contracts

### `POST /submit`

Request: a JSON object with nonblank string `text` and `creator_id`.
`text` is limited to 10,000 characters; `creator_id` to 128 characters.
Successful response (200): `content_id` (UUID string), `guess` (`human`,
`unsure`, or `ai`), `confidence` (0–1 AI-likelihood score), `label` (full
reader-facing sentence), `model_score` and `style_score` (0–1), and
`status` (`decided`). Malformed requests return JSON `error` and `message`
with HTTP 400; oversized text returns HTTP 413. A model load failure returns
JSON with HTTP 503 and is not logged as a decision.

### `POST /appeal`

Request: a JSON object with `content_id` and nonblank string `reasoning`
(at most 2,000 characters). Successful response (200): `content_id`,
`status` (`under_review`), and a confirmation message. An unknown id returns
404; malformed fields return 400. A successful appeal appends a log event with
the original `creator_id` and the writer's reasoning. It does not re-score.

## Initial scoring rule

The model signal has weight 0.60 and the style signal 0.40. When they differ
by at least 0.35, the weighted score's distance from 0.5 is halved. The
human label covers scores at or below 0.30, the AI label scores at or above
0.75, and all scores between are unsure. These are hypotheses to test with
real submissions; the next unit will measure the targets in `criteria.md`.
