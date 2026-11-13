"""The public submit contract when one creator sends a burst."""

import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

import app as service
import config
import detector


class RateLimitTests(unittest.TestCase):
    def test_eleventh_submission_is_json_429_and_audited(self):
        creator_id = f"rate-test-{uuid.uuid4()}"
        with tempfile.TemporaryDirectory() as directory:
            log_dir = Path(directory)
            with (
                patch.object(config, "LOG_DIR", log_dir),
                patch.object(config, "AUDIT_LOG", log_dir / "audit.jsonl"),
                patch.object(detector, "model_signal", return_value=0.5),
            ):
                client = service.app.test_client()
                body = {"text": "A writer submitted an ordinary paragraph for review.",
                        "creator_id": creator_id}
                statuses = [client.post("/submit", json=body).status_code
                            for _ in range(11)]
                self.assertEqual(statuses, [200] * 10 + [429])

                rejection = client.get("/log").get_json()["entries"][-1]
                self.assertEqual(rejection["creator_id"], creator_id)
                self.assertEqual(rejection["status"], "rejected")
                self.assertEqual(rejection["reason"], "rate_limited")
                self.assertTrue(rejection["timestamp"])


if __name__ == "__main__":
    unittest.main()
