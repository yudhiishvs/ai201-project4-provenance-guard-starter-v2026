"""A submission leaves enough evidence to inspect a completed local run."""

import hashlib
import json
import tempfile
import unittest
import uuid
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

    def run_entries(self):
        path = self.log_dir / "runs.jsonl"
        self.assertTrue(path.exists(), "A rejected run must leave a record")
        return [json.loads(line) for line in path.read_text().splitlines()]

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
        for field, value in response.get_json().items():
            self.assertIn(field, entry["output"])
            self.assertEqual(entry["output"][field], value)
        self.assertNotIn(submitted_text, run_file.read_text())

    def test_invalid_submission_records_its_rejection(self):
        response = self.client.post(
            "/submit", json={"creator_id": "bad-input-writer", "text": "   "}
        )

        self.assertEqual(response.status_code, 400)
        entries = self.run_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["input"]["creator_id"], "bad-input-writer")
        self.assertEqual(entries[0]["output"]["http_status"], 400)
        self.assertEqual(entries[0]["output"]["error"], "invalid_text")
        self.assertEqual(entries[0]["output"].get("message"), response.get_json()["message"])
        self.assertGreaterEqual(entries[0]["duration_ms"], 0)

    def test_rate_limited_submission_records_the_429(self):
        creator_id = f"capstone-rate-{uuid.uuid4()}"
        with patch.object(detector, "model_signal", return_value=0.5):
            responses = [
                self.client.post(
                    "/submit", json={"creator_id": creator_id, "text": "A short ordinary test passage."}
                )
                for _ in range(11)
            ]

        self.assertEqual([response.status_code for response in responses], [200] * 10 + [429])
        entries = self.run_entries()
        self.assertEqual(len(entries), 11)
        self.assertEqual(entries[-1]["output"]["http_status"], 429)
        self.assertEqual(entries[-1]["output"]["error"], "rate_limited")

    def test_detector_failure_records_the_503(self):
        with patch.object(detector, "model_signal", side_effect=detector.DetectorUnavailable("offline")):
            response = self.client.post(
                "/submit", json={"creator_id": "offline-writer", "text": "A valid passage."}
            )

        self.assertEqual(response.status_code, 503)
        entries = self.run_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["output"]["http_status"], 503)
        self.assertEqual(entries[0]["output"]["error"], "detector_unavailable")


if __name__ == "__main__":
    unittest.main()
