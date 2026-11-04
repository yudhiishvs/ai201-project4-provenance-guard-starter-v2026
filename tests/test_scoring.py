import unittest

import scoring


class ScoringTests(unittest.TestCase):
    def test_two_strong_ai_signals_cross_ai_threshold(self):
        self.assertGreaterEqual(scoring.combine_signals(0.90, 0.85), 0.75)

    def test_strong_disagreement_stays_unsure(self):
        score = scoring.combine_signals(0.95, 0.10)
        self.assertAlmostEqual(score, 0.555)
        self.assertEqual(scoring.score_to_label(score)[0], "unsure")

    def test_weak_and_strong_ai_scores_get_different_labels(self):
        self.assertEqual(scoring.score_to_label(0.51)[0], "unsure")
        self.assertEqual(scoring.score_to_label(0.95)[0], "ai")
        self.assertEqual(scoring.score_to_label(0.10)[0], "human")

    def test_every_score_on_a_hundredth_grid_gets_one_full_label(self):
        for step in range(101):
            guess, label = scoring.score_to_label(step / 100)
            self.assertIn(guess, {"human", "unsure", "ai"})
            self.assertGreater(len(label.split()), 5)
            self.assertNotIn("PLACEHOLDER", label)


if __name__ == "__main__":
    unittest.main()
