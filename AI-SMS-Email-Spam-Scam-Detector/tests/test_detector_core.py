import unittest

from detector_core import (
    clean_text,
    combine_risk_score,
    detect_categories,
    extract_urls,
    sender_reputation,
    suspicious_term_count,
    url_risk,
)


class DetectorCoreTests(unittest.TestCase):
    def test_clean_text_normalizes_urls_and_case(self):
        cleaned = clean_text("VERIFY NOW at https://bit.ly/offer!!")
        self.assertIn("urltoken", cleaned)
        self.assertEqual(cleaned, cleaned.lower())

    def test_extract_urls(self):
        urls = extract_urls("Check http://abc.com and www.xyz.in now")
        self.assertEqual(len(urls), 2)

    def test_sender_reputation(self):
        self.assertEqual(sender_reputation("alerts@sbi.co.in"), "trusted")
        self.assertEqual(sender_reputation("winner-offer@gmail.com"), "suspicious")

    def test_url_risk(self):
        self.assertEqual(url_risk("https://bit.ly/freegift"), "high")
        self.assertEqual(url_risk("https://very-long-safe-domain-example-with-many-chars.com/path/to/a/resource/and-more"), "medium")

    def test_category_and_terms(self):
        text = "Urgent verify your bank login and share otp"
        categories = detect_categories(text)
        self.assertIn("phishing", categories)
        self.assertGreater(suspicious_term_count(text), 0)

    def test_combined_risk_score_bounds(self):
        score = combine_risk_score(0.99, "suspicious", [("https://bit.ly/x", "high")], 10)
        self.assertLessEqual(score, 100.0)
        self.assertGreaterEqual(score, 0.0)


if __name__ == "__main__":
    unittest.main()
