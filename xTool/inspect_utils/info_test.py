import os
import unittest

from xTool.inspect_utils.info import Info
from xTool.testing import test_components as tc

BASEDIR = os.path.dirname(os.path.dirname(__file__))


class TestInfo(unittest.TestCase):
    def testInfoOne(self):
        info = Info(1)
        self.assertEqual(info.get('type_name'), 'int')
        self.assertEqual(info.get('file'), None)
        self.assertEqual(info.get('line'), None)
        self.assertEqual(info.get('string_form'), '1')

    def testInfoClass(self):

        info = Info(tc.NoDefaults)
        self.assertEqual(info.get('type_name'), 'type')
        assert os.path.join(BASEDIR, "testing/test_components.py") == info.get('file')
        self.assertGreater(info.get('line'), 0)

    def testInfoClassNoInit(self):
        info = Info(tc.OldStyleEmpty)
        self.assertEqual(info.get('type_name'), 'type')
        assert os.path.join(BASEDIR, "testing/test_components.py") == info.get('file')
        self.assertGreater(info.get('line'), 0)

    def testInfoNoDocstring(self):
        info = Info(tc.NoDefaults)
        self.assertEqual(info['docstring'], None, 'Docstring should be None')
