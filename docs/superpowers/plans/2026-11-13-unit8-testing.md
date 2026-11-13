# Provenance Guard Unit 8 Testing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the filed five-criterion, three-trial before/after evaluation against the staff attack set with one measured detector improvement.

**Architecture:** Preserve the Unit 7 service and criteria. Enable its prepared Flask-Limiter and audit path first. Freeze evaluation inputs before the initial run, record every outcome, diagnose misses, make exactly one service change, then rerun identical inputs and write the evidence into the README.

**Tech Stack:** Python 3.13, Flask 3, Flask-Limiter 3, local GPT-2, unittest, CSV/JSONL/Markdown.

**Spec:** The user's pasted “Show What You Know: Provenance Guard, Part 2 — Testing” assignment and this repository's `criteria.md`.

## Global Constraints

- Keep the existing repository, its history, five original criteria, and model.
- The rate limiter, audit logging, and one diagnosis-driven improvement are the only service changes.
- Do not inspect attack text before the first full attack run; inspect headers only after Milestone 1.
- Freeze provenance-labelled samples before the before run. Do not claim AI-authored text is the user's writing.
- Run all five criteria three times each before and after the improvement. Preserve exact JSON output and all attack outcomes.
- Make at least four local Unit 8 commits. Do not push without user authorization.

## Review Focus

- A non-object JSON request must get a logged JSON 400, even with the limiter enabled.
- The same creator must receive 429 after ten quick submissions, with an audit rejection.
- Missing creator IDs should not crash the limiter key function.
- Appeal evaluation must preserve original decision fields and the submitted reasoning.
- Repeated malformed evaluation requests must be interpreted separately from rate-limit rejections.

---

### Task 1: Enable and prove instrumentation

**Files:** `config.py`, `app.py`, `tests/test_rate_limit.py`, `README.md`, `results/flood_*.md`, `logs/audit.jsonl`.

**Interfaces:** Keep `POST /submit`, `GET /health`, `GET /log`, and `audit.log_rejection` signatures. Use 10/minute and 200/day per valid creator ID, falling back to address for malformed or absent IDs.

- [x] Add a service test for ten accepted submissions, then a JSON 429 and rejection log on the eleventh, and for malformed JSON to remain a JSON 400 when under limit.
- [x] Run that test and confirm it fails because limiting is off.
- [x] Enable `RATE_LIMITING_ENABLED` and the existing decorator, leaving scoring and labels untouched.
- [x] Run the focused test and the complete existing test suite; inspect one nine-field decision and one rejection through `/log`.
- [x] Run `python run_attacks.py --flood 15` against the local service; record status codes and the chosen-limit explanation.
- [x] Commit instrumentation and evidence.

### Task 2: Freeze scenarios and run the unmodified detector

**Files:** `scenarios.py`, `run_eval.py`, sample fixtures, `results/`, `logs/audit.jsonl`, `README.md`.

**Interfaces:** Keep `python run_eval.py --label before|after`; add only evaluation support needed for the existing criteria, including appeal actions and label-grid checks. Use the same frozen inputs in both runs.

- [x] Record 20 user-supplied pieces represented as own writing (five plain), ten known AI pieces, ten known human pieces, at least 12 mixed-provenance pieces, ten valid appeals, and six specified malformed bodies before testing.
- [x] Add a failing evaluation test for criterion-specific output, including appeal evidence and the label grid; then implement runner support and run the full suite.
- [x] After Task 1, unpack the staff zip into the repo, read headers only, and run every attack once with `--label before`.
- [x] Run all five criteria with three trials using `--label before` and retain the generated report.
- [x] Classify every attack, calculate the criterion verdicts, paste real output and ten audit entries including a rejection, and diagnose every miss.
- [x] Commit frozen scenarios and before-run evidence.

### Task 3: One improvement and the matching after run

**Files:** Exactly one detector behavior location among `app.py`, `scoring.py`, `stylometry.py`, `detector.py`, or `config.py`; its relevant test; `results/`; `README.md`.

**Interfaces:** Preserve response and audit field names. Choose the single change from the measured diagnosis, and document its exact value or validation rule.

- [x] Write a focused failing test for the one observed failure mechanism, then make the smallest service change that addresses it.
- [x] Run the focused test and full suite.
- [x] Run the complete attack set with `--label after` and all five frozen criteria with `--label after`.
- [x] Place before and after outcomes side by side and state gains and regressions.
- [x] Commit the improvement and after-run evidence.

### Task 4: Finish the evidence and audit

**Files:** `README.md`, `criteria.md` only if an original target is genuinely unmeasurable, `logs/audit.jsonl`, `results/`.

**Interfaces:** Keep all original criterion targets and all evidence as pasted text.

- [x] Verify every attack has an outcome and held/broke mark and every criterion has three before and three after trials with MET/MISSED verdicts.
- [x] Explain every remaining failure, next fix, reason for stopping, and the production trade in two sentences; update “How I Used AI.”
- [x] Run `python test.py`, the full unittest suite, and audit the README against the submission checklist.
- [x] Make the fourth local commit and report the branch, commit range, evidence files, and any unavailable input honestly.
