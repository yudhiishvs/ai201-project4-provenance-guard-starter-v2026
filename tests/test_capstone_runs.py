"""A submission leaves enough evidence to inspect a completed local run."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app as service
import config
import detector


class CapstoneRunTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_dir = Path(self.temp_dir.name)
        self.log_dir_patch = patch.object(config, "LOG_DIR", self.log_dir)
        self.audit_file_patch = patch.object(config, "AUDIT_LOG", self.log_dir / "audit.jsonl")
        self.log_dir_patch.start()
        self.audit_file_patch.start()
        self.client = service.app.test_client()

    def tearDown(self):
        self.audit_file_patch.stop()
        self.log_dir_patch.stop()
        self.temp_dir.cleanup()

    def test_successful_submission_writes_timed_structured_run(self):
        submitted_text = "This passage explains a routine observation in plain language."
        with patch.object(detector, "model_signal", return_value=0.5):
            response = self.client.post(
                "/submit", json={"creator_id": "capstone-writer", "text": submitted_text}
            )

        self.assertEqual(response.status_code, 200)
        run_file = self.log_dir / "runs.jsonl"
        self.assertTrue(run_file.exists())
        entries = [json.loads(line) for line in run_file.read_text().splitlines()]
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertTrue(entry["timestamp"])
        self.assertGreaterEqual(entry["duration_ms"], 0)
        self.assertEqual(entry["input"]["creator_id"], "capstone-writer")
        self.assertEqual(entry["input"]["text_chars"], len(submitted_text))
        self.assertEqual(
            entry["input"]["text_sha256"], hashlib.sha256(submitted_text.encode()).hexdigest()
        )
        self.assertEqual(entry["output"]["http_status"], 200)
        self.assertEqual(entry["output"]["content_id"], response.get_json()["content_id"])
        self.assertEqual(entry["output"]["guess"], response.get_json()["guess"])
        self.assertNotIn(submitted_text, run_file.read_text())


if __name__ == "__main__":
    unittest.main()
