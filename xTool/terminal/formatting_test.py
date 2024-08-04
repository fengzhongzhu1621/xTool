# Copyright (C) 2018 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for formatting.py."""

import unittest

from xTool.strings import formatting


class FormattingTest(unittest.TestCase):
    def test_bold(self):
        text = formatting.bold("hello")
        self.assertIn(text, ["hello", "\x1b[1mhello\x1b[0m"])

    def test_underline(self):
        text = formatting.underline("hello")
        self.assertIn(text, ["hello", "\x1b[4mhello\x1b[0m"])

    def test_indent(self):
        text = formatting.indent("hello", spaces=2)
        self.assertEqual("  hello", text)

    def test_indent_multiple_lines(self):
        text = formatting.indent("hello\nworld", spaces=2)
        self.assertEqual("  hello\n  world", text)
