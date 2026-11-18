"""Run the frozen capstone trials against the documented local service."""

import argparse
import hashlib
import json
import os
import platform
import shlex
import shutil
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path

import requests

from scenarios import HUMAN_TEXTS, SCENARIOS


ROOT = Path(__file__).resolve().parent
RUN_LOG = ROOT / "logs/runs.jsonl"
URL = "http://127.0.0.1:5000"
START_COMMAND = (
    "HF_HUB_OFFLINE=1 ./.venv/bin/gunicorn app:app "
    "--bind 127.0.0.1:5000 --workers 1 --threads 1"
)
TARGETS = (3, 10, 9, 5, 9)
DECISION_FIELDS = ("guess", "label", "confidence", "model_score", "style_score")

LOG_TEXTS = (
    "The community garden opens early on Saturdays. Volunteers water the seedlings.",
    "  The café opens at seven. Someone is already setting out the chairs.  ",
    "In the afternoon, the rain stopped.\nThe path through the park was still wet.",
    'The librarian said, "The reading room closes at six." We packed our bags.',
    "Nearly everyone took the stairs. The elevator was still being inspected.",
    "A small mistake in the map sent us to the east entrance instead of the west.",
    "The market moved indoors during the storm, and the vendors stayed until noon.",
    "I checked the schedule twice before writing the departure time on a note.",
    "The old clock runs a little slow. We set it again after changing the battery.",
    "A green light and a short chime told us the machine had finished its cycle.",
)
REJECTIONS = (
    ("empty-body", b"", 400, "invalid_json"),
    ("malformed-json", b"{", 400, "invalid_json"),
    ("blank-text", {"creator_id": "capstone-blank", "text": " \t "}, 400, "invalid_text"),
    ("missing-creator", {"text": "This request has no creator identifier."}, 400, "invalid_creator_id"),
    ("oversized-text", {"creator_id": "capstone-large", "text": "x" * 10_001}, 413, "text_too_long"),
)


def prior_decisions():
    """Match the first ten mixed inputs to the earlier project's frozen output."""
    report = (ROOT / "results/run_2026-11-13_0756_after.md").read_text(encoding="utf-8")
    section = report.split("### three labels and hundredth grid\n", 1)[1]
    first_trial = section.split("```json\n", 1)[1].split("```", 1)[0]
    pairs = list(zip(SCENARIOS[2]["texts"][:10], json.loads(first_trial)[:10], strict=True))
    if len(pairs) != 10 or any(row["status"] != 200 or row["sent"] != text[:70] for text, row in pairs):
        raise ValueError("Unit 8 input order or expected output did not match.")
    return pairs


def log_lines():
    return RUN_LOG.read_bytes().splitlines() if RUN_LOG.exists() else []


def submit(client, name, payload):
    """Keep the response and the line reference for this individual request."""
    wire = payload if isinstance(payload, bytes) else json.dumps(
        payload, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    previous_lines = len(log_lines())
    began = time.perf_counter_ns()
    row = {"case": name, "body_bytes": len(wire)}
    try:
        response = client.post(
            f"{URL}/submit", data=wire, headers={"Content-Type": "application/json"},
            timeout=45,
        )
        row["http_status"] = response.status_code
        row["response"] = response.json() if response.headers.get(
            "Content-Type", ""
        ).startswith("application/json") else response.text
    except requests.RequestException as exc:
        row["http_status"] = None
        row["response"] = {"client_error": str(exc)}
    row["client_ms"] = round((time.perf_counter_ns() - began) / 1_000_000, 3)
    new_lines = log_lines()[previous_lines:]
    row["log_count"] = len(new_lines)
    row["log_line"] = previous_lines + 1 if len(new_lines) == 1 else None
    record = {}
    if len(new_lines) == 1:
        try:
            decoded = json.loads(new_lines[0])
            if isinstance(decoded, dict):
                record = decoded
        except (UnicodeDecodeError, ValueError):
            pass
    return row, record


def submission(creator_id, text):
    return {"creator_id": creator_id, "text": text}


def decision_returned(row):
    response = row["response"]
    return (
        row["http_status"] == 200 and isinstance(response, dict)
        and response.get("status") == "decided" and bool(response.get("content_id"))
    )


def structured(record):
    try:
        datetime.fromisoformat(record["timestamp"])
        return (
            isinstance(record["input"], dict) and isinstance(record["output"], dict)
            and isinstance(record["output"]["http_status"], int)
            and isinstance(record["duration_ms"], (int, float))
        )
    except (KeyError, TypeError, ValueError):
        return False


def measure_logging(client, trial):
    rows = []
    for i, text in enumerate(LOG_TEXTS, 1):
        name = f"capstone-log-{trial}-{i:02}"
        row, record = submit(client, name, submission(name, text))
        row["structured"] = structured(record)
        expected_input = {
            "creator_id": name,
            "text_chars": len(text),
            "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "body_bytes": row["body_bytes"],
            "content_type": "application/json",
        }
        output = record["output"] if row["structured"] else {}
        response = row["response"]
        row["input_matches"] = record.get("input") == expected_input
        row["mismatched_response_fields"] = (
            sorted(key for key, value in response.items() if key not in output or output[key] != value)
            if isinstance(response, dict) else ["json"]
        )
        row["accurate"] = (
            row["structured"] and row["input_matches"] and row["http_status"] is not None
            and output.get("http_status") == row["http_status"]
            and not row["mismatched_response_fields"] and record["duration_ms"] >= 0
        )
        rows.append(row)
    return rows


def wait_until_ready(client, server):
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline and server.poll() is None:
        try:
            response = client.post(f"{URL}/ping", json={"message": "trial startup"}, timeout=1)
            if response.ok and response.json().get("service") == "provenance-guard":
                return response.json()
        except requests.RequestException:
            pass
        time.sleep(0.1)
    raise RuntimeError("The documented server command did not become ready.")


def worker_cpu_snapshot(server):
    """Read combined user and system CPU time from the sole Gunicorn worker."""
    try:
        worker_pid = subprocess.check_output(["pgrep", "-P", str(server.pid)], text=True).strip()
        readout = subprocess.check_output(["ps", "-o", "time=", "-p", worker_pid], text=True).strip()
        seconds = sum(float(part) * 60**power for power, part in enumerate(reversed(readout.split(":"))))
    except (OSError, subprocess.CalledProcessError, ValueError):
        return None
    return {"pid": int(worker_pid), "readout": readout, "cpu_seconds": seconds}


def trial_requests(client, server, trial, fixtures, startup):
    execution = []
    for i, text in enumerate(HUMAN_TEXTS[:3], 1):
        name = f"capstone-start-{trial}-{i:02}"
        row, _ = submit(client, name, submission(name, text))
        row["passed"] = decision_returned(row)
        execution.append(row)

    cpu_before = worker_cpu_snapshot(server)
    logging = measure_logging(client, trial)
    cpu_after = worker_cpu_snapshot(server)

    failures = []
    for name, body, status, error in REJECTIONS:
        row, record = submit(client, name, body)
        try:
            health = client.get(f"{URL}/health", timeout=5)
            row["health_after"] = {"http_status": health.status_code, "response": health.json()}
        except requests.RequestException as exc:
            row["health_after"] = {"http_status": None, "response": {"client_error": str(exc)}}
        row["expected"] = {"http_status": status, "error": error}
        row["passed"] = (
            row["http_status"] == status and isinstance(row["response"], dict)
            and row["response"].get("error") == error and structured(record)
            and record["output"]["http_status"] == status and record["output"].get("error") == error
            and server.poll() is None and row["health_after"]["http_status"] == 200
            and row["health_after"]["response"].get("detector_loaded") is True
        )
        failures.append(row)

    preservation = []
    for i, (text, expected) in enumerate(fixtures, 1):
        name = f"capstone-prior-{trial}-{i:02}"
        row, _ = submit(client, name, submission(name, text))
        row["expected"] = {key: expected[key] for key in DECISION_FIELDS}
        row["passed"] = decision_returned(row) and all(
            row["response"].get(key) == value for key, value in row["expected"].items()
        )
        preservation.append(row)

    return {
        "trial": trial,
        "startup_response": startup,
        "worker_cpu": {"before_warm_batch": cpu_before, "after_warm_batch": cpu_after},
        "counts": [
            sum(row["passed"] for row in execution),
            sum(row["structured"] for row in logging),
            sum(row["accurate"] for row in logging),
            sum(row["passed"] for row in failures),
            sum(row["passed"] for row in preservation),
        ],
        "execution": execution,
        "logging": logging,
        "failures": failures,
        "preservation": preservation,
    }


def run_trial(number, fixtures):
    offline_flag, *command = shlex.split(START_COMMAND)
    offline_key, offline_value = offline_flag.split("=", 1)
    environment = {
        **os.environ,
        offline_key: offline_value,
        "AI201_DETECTOR_MODEL": "gpt2",
        "AI201_RATE_LIMITS": "1",
    }
    with tempfile.TemporaryFile() as server_log, requests.Session() as client:
        client.trust_env = False
        with subprocess.Popen(
            command, cwd=ROOT, env=environment, stdout=server_log, stderr=subprocess.STDOUT,
        ) as server:
            try:
                startup = wait_until_ready(client, server)
                return trial_requests(client, server, number, fixtures, startup)
            except Exception:
                server_log.seek(0)
                print(server_log.read().decode("utf-8", errors="replace"))
                raise
            finally:
                server.terminate()
                try:
                    server.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    server.kill()
                    server.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("before", "after"))
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    evidence = args.output_dir / f"capstone-{args.phase}.json"
    raw_log = args.output_dir / f"capstone-{args.phase}-runs.jsonl"
    if RUN_LOG.exists() or evidence.exists() or raw_log.exists():
        parser.error("Use a fresh checkout without a runs.jsonl file and a new evidence destination.")
    if START_COMMAND not in (ROOT / "RUNNING.md").read_text(encoding="utf-8").splitlines():
        parser.error("The startup command must match RUNNING.md.")

    fixtures = prior_decisions()
    revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    trials = []
    for number in range(1, 4):
        trial = run_trial(number, fixtures)
        trials.append(trial)
        print(f"{args.phase}, trial {number}: {trial['counts']}", flush=True)
    verdicts = [
        "MET" if all(trial["counts"][i] >= target for trial in trials) else "MISSED"
        for i, target in enumerate(TARGETS)
    ]

    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "phase": args.phase,
        "revision": revision,
        "environment": f"{platform.system()} {platform.machine()}, Python {platform.python_version()}",
        "start_command": START_COMMAND,
        "verdicts": verdicts,
        "trials": trials,
    }
    with evidence.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    shutil.copyfile(RUN_LOG, raw_log)
    print(" ".join(verdicts))


if __name__ == "__main__":
    main()
