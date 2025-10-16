import unittest

from xTool.utils.tests import *


class TestTests(unittest.TestCase):
    @skipUnlessImported("xTool.utils.tests", "skipUnlessImported")
    def test_skipUnlessImported(self):
        self.assertEqual(1, 1)

    @skipUnlessImported("xTool.utils.tests1", "skipUnlessImported")
    def test_skipUnlessImported2(self):
        self.assertEqual(1, 2)

    def test_assertEqualIgnoreMultipleSpaces(self):
        first = "1 2"
        second = " 1    2\n\t   "
        res = assertEqualIgnoreMultipleSpaces(self, first, second, msg="I'm message")
        self.assertEqual(res, None)
