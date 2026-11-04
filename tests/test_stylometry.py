import unittest

import stylometry


class StylometryTests(unittest.TestCase):
    def test_sentence_length_spread_handles_one_sentence_and_variation(self):
        self.assertEqual(stylometry.sentence_length_spread("Just one sentence."), 0.0)
        self.assertGreater(
            stylometry.sentence_length_spread("Go. Now walk all the way home."),
            0.0,
        )

    def test_type_token_ratio_counts_unique_words(self):
        self.assertEqual(stylometry.type_token_ratio("cat cat dog bird"), 0.75)

    def test_punctuation_density_counts_expressive_marks_per_word(self):
        self.assertAlmostEqual(stylometry.punctuation_density("Hi, you; yes?"), 1.0)

    def test_repetitive_regular_prose_looks_more_ai_like_than_varied_prose(self):
        regular = (
            "The system works well. The system works well. The system works well. "
            "The system works well. The system works well. The system works well."
        )
        varied = (
            "Rain. My grandmother hurried through the market; six umbrellas "
            "collided, and the baker shouted, 'Mind the apricots!' By dusk, "
            "we carried home a crooked loaf and a wonderfully absurd story."
        )
        self.assertGreater(stylometry.style_signal(regular), stylometry.style_signal(varied))

    def test_empty_and_very_short_text_is_neutral(self):
        self.assertEqual(stylometry.style_signal(""), 0.5)
        self.assertEqual(stylometry.style_signal("Hello world."), 0.5)


if __name__ == "__main__":
    unittest.main()
