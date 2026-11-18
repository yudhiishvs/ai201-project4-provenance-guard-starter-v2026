# Capstone: observable local runs

## Scope

Extend the existing Provenance Guard service with one operational layer: a reproducible local server command and a structured, timed record for each submission. Keep the detector, scoring, labels, rate limits, and appeal behavior unchanged. Use Shape A and local Path B.

## Sequence

1. Record the chosen scope and its exclusions in the README; commit that decision.
2. Write failing tests for a submission run record, then add the JSONL writer; run the service suite and commit.
3. Write failing route tests for successful, rejected, and rate-limited submissions; add request timing and output capture; run the suite and commit.
4. Add one local start command and document the exact environment and model requirement; verify the command and commit the build.
5. Receive the five acceptance criteria directly from the student. Check them for testability without rewriting them; commit them with a message naming the criteria before any capstone evaluation results.
6. From a clean checkout, start the service and record at least ten real requests, a failure, and measured per-run compute time. Commit the first results with a message naming them.
7. Run all five criteria in three separate trials, preserve real output and verdicts, then choose one improvement from an observed miss and commit it.
8. Repeat all five trials three times, record both tables and diagnoses, calculate cost at 100 users per day, and finish all nine README sections. Verify the suite, logs, history, and branch name before the final commit.

## Evidence rules

Keep the user-authored criteria unchanged except for formatting. Do not claim a measurement that did not run. Keep local test artifacts separate from prior units' audit evidence. Do not push without an explicit request.

## Fixed evaluation method

Use `capstone_eval.py` from a clean checkout for each phase. Each phase runs
three trials. Each trial starts a new single-worker Gunicorn process with the
command in RUNNING.md, local GPT-2, and the existing rate limits enabled.
Apply each target independently to all three trials. A criterion is MET
when every trial reaches the target.

1. Send the first three Unit 8 personal samples to the newly started service.
   Count HTTP 200 responses with a decision status and content ID.
2. Send ten valid, fixed passages with distinct creator IDs. Each request
   counts when it appends exactly one parseable JSON record with a timestamp,
   input object, output object, numeric duration, and HTTP status.
3. Score the same ten requests against their corresponding records. Compare
   creator ID, exact text length and SHA-256 fingerprint, body byte count, and
   content type with the request. Compare HTTP status and every returned
   JSON field with the output object. Require a nonnegative duration. The
   input fingerprint checks the exact text without saving it in the run log.
4. Send an empty body, malformed JSON, blank text, a missing creator ID, and
   oversized text. Require the expected HTTP 400 or 413 and error code in
   both the response and its single structured record. Check that the server
   still answers `/health` with its model loaded after each rejection.
5. Replay the first ten mixed-provenance submissions from the earlier Unit 8
   evaluation. Compare the HTTP decision, guess, label, combined score, and
   both signal scores with the committed first-trial output under
   “three labels and hundredth grid.” IDs are newly assigned per request.

For cost, use the ten warm submissions in criterion 2 of the first after
trial. Read accumulated user and system CPU time for the Gunicorn worker
immediately before and after the batch. Divide the difference by ten and
multiply that per-run figure by 100 for one submission per person per day.
The same requests also retain client elapsed time as a measured fallback
when the host does not expose worker CPU time.
