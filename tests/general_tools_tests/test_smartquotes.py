from __future__ import absolute_import, unicode_literals, print_function
import unittest
from libraries.general_tools import smartquotes


@unittest.skip("smartquotes not working on lambda")
class SmartquotesTests(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(smartquotes.smartquotes(""), "")

    def test_multiple_lines(self):
        self.assertEqual(
            smartquotes.smartquotes("The quick brown fox jumped\nover\nthe lazy\n\tdog."),
            "The quick brown fox jumped over the lazy dog.")
