"""Criterion-specific evaluation records real route and label behavior."""

import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

import app as service
import config
import detector
import run_eval
import scenarios


class EvaluationTests(unittest.TestCase):
    def test_non_object_json_body_is_a_valid_malformed_scenario(self):
        scenario = {"name": "non-object JSON", "criterion": 5, "bodies": [[]]}
        with patch.object(scenarios, "SCENARIOS", [scenario]):
            self.assertEqual(scenarios.validate(), [])
        self.assertEqual(run_eval.bodies_for(scenario), [[]])
        self.assertEqual(run_eval.describe([]), "[]")

    def test_appeal_trial_records_preserved_decision_and_unknown_id(self):
        self.assertIsNotNone(getattr(run_eval, "run_appeal_trial", None))
        with tempfile.TemporaryDirectory() as directory:
            log_dir = Path(directory)
            with (
                patch.object(config, "LOG_DIR", log_dir),
                patch.object(config, "AUDIT_LOG", log_dir / "audit.jsonl"),
                patch.object(detector, "model_signal", return_value=0.5),
            ):
                client = service.app.test_client()

                def post(path, body):
                    response = client.post(path, json=body)
                    return response.status_code, response.get_json()

                def get(path):
                    return client.get(path).get_json()

                scenario = {
                    "name": f"appeals-{uuid.uuid4()}",
                    "texts": ["A writer submitted a paragraph and requested a review."],
                    "reasoning": "I wrote this paragraph myself.",
                }
                rows = run_eval.run_appeal_trial(scenario, post, get)

        self.assertEqual(len(rows), 2)
        valid, unknown = rows
        self.assertEqual(valid["submit_status"], 200)
        self.assertEqual(valid["appeal_status"], 200)
        self.assertEqual(valid["appeal_response"]["status"], "under_review")
        self.assertTrue(valid["original_preserved"])
        self.assertTrue(valid["reasoning_recorded"])
        self.assertTrue(valid["content_id"])
        self.assertEqual(unknown["appeal_status"], 404)
        self.assertFalse(unknown["appeal_event_written"])

    def test_score_grid_reports_all_three_labels_without_gaps(self):
        self.assertIsNotNone(getattr(run_eval, "score_grid", None))
        result = run_eval.score_grid()
        self.assertEqual(result["scores_checked"], 101)
        self.assertEqual(result["labels_seen"], ["ai", "human", "unsure"])
        self.assertEqual(result["invalid_scores"], [])


if __name__ == "__main__":
    unittest.main()
