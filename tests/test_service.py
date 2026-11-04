import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app as service
import audit
import config
import detector


REGULAR_TEXT = (
    "The system works well. The system works well. The system works well. "
    "The system works well. The system works well. The system works well."
)


class ServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        log_dir = Path(self.temp_dir.name)
        self.log_dir_patch = patch.object(config, "LOG_DIR", log_dir)
        self.log_file_patch = patch.object(config, "AUDIT_LOG", log_dir / "audit.jsonl")
        self.log_dir_patch.start()
        self.log_file_patch.start()
        self.client = service.app.test_client()

    def tearDown(self):
        self.log_file_patch.stop()
        self.log_dir_patch.stop()
        self.temp_dir.cleanup()

    def test_submit_returns_real_style_score_and_audits_decision(self):
        with patch.object(detector, "model_signal", return_value=0.90):
            response = self.client.post(
                "/submit", json={"text": REGULAR_TEXT, "creator_id": "writer-1"}
            )

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertEqual(body["guess"], "ai")
        self.assertEqual(body["model_score"], 0.90)
        self.assertEqual(body["style_score"], 1.0)
        self.assertEqual(body["confidence"], 0.94)
        self.assertIn("appeal", body["label"])
        self.assertEqual(body["status"], "decided")
        self.assertTrue(body["content_id"])

        entry = audit.read_entries()[0]
        self.assertEqual(entry["content_id"], body["content_id"])
        self.assertEqual(entry["creator_id"], "writer-1")
        self.assertEqual(entry["combined_score"], body["confidence"])
        self.assertEqual(entry["model_score"], body["model_score"])
        self.assertEqual(entry["style_score"], body["style_score"])
        self.assertEqual(entry["status"], "decided")
        self.assertTrue(entry["timestamp"])

    def test_appeal_adds_review_event_without_overwriting_decision(self):
        with patch.object(detector, "model_signal", return_value=0.90):
            submitted = self.client.post(
                "/submit", json={"text": REGULAR_TEXT, "creator_id": "writer-1"}
            ).get_json()
        original = audit.read_entries()[0].copy()

        response = self.client.post(
            "/appeal",
            json={"content_id": submitted["content_id"], "reasoning": "I wrote this."},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "under_review")
        self.assertEqual(response.get_json()["content_id"], submitted["content_id"])
        entries = self.client.get("/log").get_json()["entries"]
        self.assertEqual(entries[0], original)
        self.assertEqual(entries[1]["event"], "appeal")
        self.assertEqual(entries[1]["status"], "under_review")
        self.assertEqual(entries[1]["reasoning"], "I wrote this.")
        self.assertEqual(entries[1]["creator_id"], "writer-1")

    def test_bad_submissions_return_json_errors_and_no_decisions(self):
        invalid = [
            ([], 400),
            ({"creator_id": "writer"}, 400),
            ({"text": "   ", "creator_id": "writer"}, 400),
            ({"text": 123, "creator_id": "writer"}, 400),
            ({"text": "This is enough text.", "creator_id": ""}, 400),
            ({"text": "x" * 10001, "creator_id": "writer"}, 413),
        ]
        with patch.object(detector, "model_signal", side_effect=AssertionError("invalid input reached detector")):
            for payload, expected_status in invalid:
                with self.subTest(payload=payload if len(str(payload)) < 100 else "oversized"):
                    response = self.client.post("/submit", json=payload)
                    self.assertEqual(response.status_code, expected_status)
                    self.assertIn("error", response.get_json())
                    self.assertIn("message", response.get_json())
        self.assertFalse(any(e.get("status") == "decided" for e in audit.read_entries()))

    def test_unknown_content_id_cannot_be_appealed(self):
        response = self.client.post(
            "/appeal", json={"content_id": "not-a-real-id", "reasoning": "I wrote it"}
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(audit.read_entries(), [])

    def test_unavailable_detector_returns_service_error_not_server_crash(self):
        with patch.object(detector, "model_signal", side_effect=detector.DetectorUnavailable("offline")):
            response = self.client.post(
                "/submit", json={"text": REGULAR_TEXT, "creator_id": "writer-1"}
            )
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()["error"], "detector_unavailable")
        self.assertFalse(any(e.get("status") == "decided" for e in audit.read_entries()))


if __name__ == "__main__":
    unittest.main()
