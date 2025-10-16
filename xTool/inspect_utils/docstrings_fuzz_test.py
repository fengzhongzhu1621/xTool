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

"""Fuzz tests for the docstring parser module."""

from hypothesis import example, given, settings
from hypothesis import strategies as st

from . import docstrings


class TestDocstringsFuzz:

    @settings(max_examples=1000, deadline=1000)  # 生成 1000个测试用例，每个用例的超时时间是 1 秒
    @given(st.text(min_size=1))
    @example('This is a one-line docstring.')  # 指定特定的测试用例
    def test_fuzz_parse(self, value):
        docstrings.parse(value)
