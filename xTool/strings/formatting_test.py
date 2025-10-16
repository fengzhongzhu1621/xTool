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

LINE_LENGTH = 80


class FormattingTest(unittest.TestCase):
    def test_wrap_one_item(self):
        lines = formatting.wrapped_join(["rice"])
        self.assertEqual(["rice"], lines)

    def test_wrap_multiple_items(self):
        lines = formatting.wrapped_join(["rice", "beans", "chicken", "cheese"], width=15)
        self.assertEqual(["rice | beans |", "chicken |", "cheese"], lines)

    def test_ellipsis_truncate(self):
        text = "This is a string"
        truncated_text = formatting.ellipsis_truncate(text=text, available_space=10, line_length=LINE_LENGTH)
        self.assertEqual("This is...", truncated_text)

    def test_ellipsis_truncate_not_enough_space(self):
        text = "This is a string"
        truncated_text = formatting.ellipsis_truncate(text=text, available_space=2, line_length=LINE_LENGTH)
        self.assertEqual("This is a string", truncated_text)

    def test_ellipsis_middle_truncate(self):
        text = "1000000000L"
        truncated_text = formatting.ellipsis_middle_truncate(text=text, available_space=7, line_length=LINE_LENGTH)
        self.assertEqual("10...0L", truncated_text)

    def test_ellipsis_middle_truncate_not_enough_space(self):
        text = "1000000000L"
        truncated_text = formatting.ellipsis_middle_truncate(text=text, available_space=2, line_length=LINE_LENGTH)
        self.assertEqual("1000000000L", truncated_text)
