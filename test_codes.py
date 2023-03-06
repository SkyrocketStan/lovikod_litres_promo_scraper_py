from unittest import TestCase

import codes


class TestCodes(TestCase):
    def test_strip_ampersand_with_amp(self):
        url = 'https://example.com/?code=ABC&ref=123'
        url_expected = 'https://example.com/?code=ABC'
        self.assertEqual(codes.strip_ampersand(url), url_expected)

    def test_strip_ampersand_without_amp(self):
        url = 'https://example.com/?code=ABC'
        url_expected = 'https://example.com/?code=ABC'
        self.assertEqual(codes.strip_ampersand(url), url_expected)
