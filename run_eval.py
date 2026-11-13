#!/usr/bin/env python3
"""
Run your five criteria three times each.  <- UNIT 8, MILESTONE 3

    python app.py                              # in one terminal
    python run_eval.py --label before          # in another
    python run_eval.py --label after

The attack set tests what staff thought to test. This tests what *you* thought
to test, and the two rarely overlap much. Both count.

Fill in `scenarios.py` first — that's where you say what each criterion needs
run against it. A criterion about false positives needs your own writing. One
about label coverage needs inputs across the score range.

!! Three trials, and **your first signal runs a model, so identical input can
score differently twice.** That's exactly why repeats matter here.

This does the sending and the recording. It does not decide whether a trial
passed — that depends on the criterion you wrote, so the Verdict column comes
back blank.
"""

import argparse
import datetime as dt
import json
import sys
import uuid
from pathlib import Path

import config
import scoring

# Windows consoles often run a codepage that can't print every character in
# this file's help text. Without this, `--help` ends in a UnicodeEncodeError
# traceback instead of the help — which is a miserable first thing to hit.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors="replace")
    except (AttributeError, ValueError):  # not a normal text stream
        pass


DEFAULT_URL = f"http://{config.HOST}:{config.PORT}"


def bodies_for(scenario):
    """
    The request bodies one scenario sends.

    A "texts" scenario gets a creator_id made up for it. A "bodies" scenario is
    sent exactly as written, which is how a bad-input criterion says things a
    string can't — no `text` field, a null, something enormous.
    """
    if scenario.get("bodies"):
        return list(scenario["bodies"])
    return [
        {"text": text, "creator_id": f"eval_{scenario['name'][:12]}_{i}"}
        for i, text in enumerate(scenario["texts"], 1)
    ]


def describe(body):
    """A short, readable note of what was sent — for the report."""
    if isinstance(body, dict) and set(body) == {"text", "creator_id"} and isinstance(body.get("text"), str):
        text = body["text"]
        return text[:70] if text else "(empty text)"
    return json.dumps(body)[:120]


def score_grid():
    """Check the full hundredth grid against the actual label mapping."""
    labels = set()
    invalid = []
    for hundredth in range(101):
        score = hundredth / 100
        try:
            guess, _label = scoring.score_to_label(score)
            if guess not in {"human", "unsure", "ai"}:
                invalid.append(score)
            else:
                labels.add(guess)
        except Exception:  # a gap is an evaluation result, not a stopped run
            invalid.append(score)
    return {
        "sent": "score_to_label grid: 0.00, 0.01, ..., 1.00",
        "scores_checked": 101,
        "labels_seen": sorted(labels),
        "invalid_scores": invalid,
    }


def run_appeal_trial(scenario, post, get):
    """Submit and appeal real content IDs, then inspect the public audit log."""
    results = []
    reasoning = scenario["reasoning"]
    for i, text in enumerate(scenario["texts"], 1):
        creator_id = f"eval_appeal_{i}"
        submit_status, submitted = post("/submit", {"text": text, "creator_id": creator_id})
        result = {"sent": text[:70], "submit_status": submit_status,
                  "content_id": submitted.get("content_id")}
        if submit_status != 200 or not result["content_id"]:
            result["submit_response"] = submitted
            results.append(result)
            continue

        content_id = result["content_id"]
        appeal_status, appeal_response = post(
            "/appeal", {"content_id": content_id, "reasoning": reasoning}
        )
        events = [entry for entry in get("/log")["entries"]
                  if entry.get("content_id") == content_id]
        decision = next((entry for entry in events if entry.get("status") == "decided"), None)
        appeal_event = next((entry for entry in events if entry.get("event") == "appeal"), None)
        required = {
            "content_id": content_id,
            "creator_id": creator_id,
            "guess": submitted["guess"],
            "model_score": submitted["model_score"],
            "style_score": submitted["style_score"],
            "combined_score": submitted["confidence"],
            "label": submitted["label"],
            "status": "decided",
        }
        result.update({
            "appeal_status": appeal_status,
            "appeal_response": appeal_response,
            "original_preserved": bool(decision and decision.get("timestamp") and
                                       all(decision.get(key) == value
                                           for key, value in required.items())),
            "reasoning_recorded": bool(appeal_event and
                                       appeal_event.get("reasoning") == reasoning and
                                       appeal_event.get("status") == "under_review"),
        })
        results.append(result)

    unknown_id = str(uuid.uuid4())
    unknown_status, unknown_response = post(
        "/appeal", {"content_id": unknown_id, "reasoning": reasoning}
    )
    unknown_events = [entry for entry in get("/log")["entries"]
                      if entry.get("content_id") == unknown_id and
                      entry.get("event") == "appeal"]
    results.append({
        "sent": "unknown content_id",
        "content_id": unknown_id,
        "appeal_status": unknown_status,
        "appeal_response": unknown_response,
        "appeal_event_written": bool(unknown_events),
    })
    return results


def run_rejection_trial(scenario, post, get):
    """Check the returned JSON and any decisions appended by each bad input."""
    results = []
    for body in scenario["bodies"]:
        before = len(get("/log")["entries"])
        status, response = post("/submit", body)
        appended = get("/log")["entries"][before:]
        results.append({
            "sent": describe(body),
            "status": status,
            "error": response.get("error"),
            "message": response.get("message"),
            "new_decisions": sum(entry.get("status") == "decided" for entry in appended),
        })
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--label", default="")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args()

    try:
        import requests
    except ImportError:
        print("The `requests` package isn't installed.\n"
              "Run: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)

    try:
        import scenarios
    except ImportError:
        print("No scenarios.py found. Milestone 3 starts by filling it in.",
              file=sys.stderr)
        sys.exit(1)

    problems = scenarios.validate()
    if problems:
        print("scenarios.py has problems:\n", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        sys.exit(1)

    try:
        requests.get(f"{args.url}/health", timeout=5)
    except Exception:  # noqa: BLE001
        print(f"Nothing answering at {args.url}. Start it:  python app.py",
              file=sys.stderr)
        sys.exit(1)

    if args.trials < 3:
        print(f"!! {args.trials} trial(s). The submission asks for three.\n")

    def post(path, body):
        response = requests.post(f"{args.url}{path}", json=body,
                                 timeout=args.timeout)
        return response.status_code, response.json()

    def get(path):
        return requests.get(f"{args.url}{path}", timeout=args.timeout).json()

    rows = []
    for scenario in scenarios.SCENARIOS:
        print(f"\n{scenario['name']}  (criterion {scenario.get('criterion') or '—'})")

        trials = []
        for trial in range(1, args.trials + 1):
            results = []
            if scenario.get("kind") == "appeal":
                try:
                    results = run_appeal_trial(scenario, post, get)
                except Exception as exc:  # noqa: BLE001
                    results.append({"status": None, "error": f"{type(exc).__name__}: {exc}",
                                    "sent": "appeal trial"})
            elif scenario.get("kind") == "rejection":
                try:
                    results = run_rejection_trial(scenario, post, get)
                except Exception as exc:  # noqa: BLE001
                    results.append({"status": None, "error": f"{type(exc).__name__}: {exc}",
                                    "sent": "rejection trial"})
            else:
                for i, body in enumerate(bodies_for(scenario), 1):
                    preview = describe(body)
                    try:
                        status, payload = post("/submit", body)
                        results.append({
                            "status": status,
                            "guess": payload.get("guess"),
                            "confidence": payload.get("confidence"),
                            "model_score": payload.get("model_score"),
                            "style_score": payload.get("style_score"),
                            "label": payload.get("label"),
                            "sent": preview,
                            "error": payload.get("error"),
                            "message": payload.get("message"),
                        })
                    except Exception as exc:  # noqa: BLE001
                        results.append({"status": None, "error": f"{type(exc).__name__}: {exc}",
                                        "sent": preview})
                if scenario.get("score_grid"):
                    results.append(score_grid())

            trials.append(results)
            guesses = [r.get("guess") or "—" for r in results]
            print(f"  trial {trial}: {', '.join(guesses)}")

        rows.append({"scenario": scenario, "trials": trials})

    write_report(rows, args)


def write_report(rows, args):
    config.RESULTS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    label = f"_{args.label}" if args.label else ""
    path = config.RESULTS_DIR / f"run_{stamp}{label}.md"

    n = args.trials
    headers = " | ".join(f"Run {i}" for i in range(1, n + 1))
    divider = "|".join(["---"] * n)

    lines = [
        f"# Run log{f' — {args.label}' if args.label else ''}",
        "",
        "- Produced by: `run_eval.py::main`",
        "- Service: `app.py::submit` · scoring: `scoring.py::combine_signals`",
        f"- {n} trials per criterion · {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "Fill in Target from `criteria.md`, and Run and Verdict from the output",
        "underneath. Whether a trial passed depends on the criterion you wrote.",
        "",
        f"| Criterion | Target | {headers} | Verdict |",
        f"|---|---|{divider}|---|",
    ]

    for row in rows:
        scenario = row["scenario"]
        number = scenario.get("criterion")
        name = f"{number}. {scenario['name']}" if number else scenario["name"]
        lines.append(f"| {name} |  | {' | '.join([' '] * n)} |  |")

    lines += ["", "---", "", "## What actually came back", "",
              "Real output. Paste the relevant parts into your README — the rubric",
              "asks for the actual JSON, not a description of it.", ""]

    for row in rows:
        scenario = row["scenario"]
        lines += [f"### {scenario['name']}", ""]
        for trial_number, results in enumerate(row["trials"], 1):
            lines += [f"**Trial {trial_number}**", "", "```json",
                      json.dumps(results, indent=2), "```", ""]

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {path.relative_to(config.ROOT)}")
    print("Commit it. It's the evidence the test actually happened.")


if __name__ == "__main__":
    main()
