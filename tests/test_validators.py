import unittest

from wordpress_ai_automation.validators import validate_html_content


class ValidatorsTest(unittest.TestCase):
    def test_validate_html_content_accepts_valid_html(self):
        html = "<h1>Title</h1>" + "<p>Paragraph text.</p>" * 80
        issues = validate_html_content(html)
        self.assertEqual([], issues)

    def test_validate_html_content_rejects_script(self):
        html = "<h1>Title</h1><p>ok</p><script>alert(1)</script>"
        issues = validate_html_content(html)
        self.assertTrue(any("forbidden" in issue.lower() for issue in issues))


if __name__ == "__main__":
    unittest.main()
