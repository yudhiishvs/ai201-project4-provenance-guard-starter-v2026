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
