import unittest

from detector_core import (
    URL_PLACEHOLDER,
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
        self.assertIn(URL_PLACEHOLDER, cleaned)
        self.assertEqual(cleaned, cleaned.lower())


    def test_clean_text_replaces_multiple_urls_with_placeholder(self):
        cleaned = clean_text("visit https://a.com now and also www.b.org/offer")
        self.assertEqual(cleaned.count(URL_PLACEHOLDER), 2)
        self.assertNotIn("https://a.com", cleaned)

    def test_extract_urls(self):
        urls = extract_urls("Check http://abc.com and www.xyz.in now")
        self.assertEqual(len(urls), 2)

    def test_sender_reputation(self):
        self.assertEqual(sender_reputation("alerts@sbi.co.in"), "trusted")
        self.assertEqual(sender_reputation("winner-offer@gmail.com"), "suspicious")

    def test_sender_reputation_spoofed_domain_not_trusted(self):
        self.assertEqual(sender_reputation("alerts@sbi.co.in.evil.com"), "suspicious")
        self.assertEqual(sender_reputation("portal.icicibank.com"), "trusted")

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
