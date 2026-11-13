"""Append a privacy-conscious record of each observed submission run."""

import hashlib
import json
import threading
from datetime import datetime, timezone

import config


_lock = threading.Lock()


def log_submission(payload, response_body, status_code, duration_ms, body_bytes, content_type):
    """Record the request and response without storing submitted prose."""
    fields = payload if isinstance(payload, dict) else {}
    submitted_text = fields.get("text")
    creator_id = fields.get("creator_id")
    output = response_body if isinstance(response_body, dict) else {}
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "input": {
            "creator_id": creator_id if isinstance(creator_id, str) else None,
            "text_chars": len(submitted_text) if isinstance(submitted_text, str) else None,
            "text_sha256": (
                hashlib.sha256(submitted_text.encode("utf-8")).hexdigest()
                if isinstance(submitted_text, str) else None
            ),
            "body_bytes": body_bytes,
            "content_type": content_type,
        },
        "output": {
            "http_status": status_code,
            "content_id": output.get("content_id"),
            "guess": output.get("guess"),
            "label": output.get("label"),
            "error": output.get("error"),
        },
        "duration_ms": round(duration_ms, 3),
    }
    path = config.LOG_DIR / "runs.jsonl"
    with _lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry
