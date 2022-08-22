# -*- coding: utf-8 -*-
import pytest
from xTool.units import PercentUnit
from xTool.units.exceptions import UnitSuffixNotFound


class TestPercentUnit:

    def test_convert(self):
        actual = PercentUnit().convert(0.1, "%", "")
        assert actual == 10
        actual = PercentUnit().convert(10, "%", "")
        assert actual == 1000
        with pytest.raises(UnitSuffixNotFound):
            PercentUnit().convert(0.1, "%%", "")
        actual = PercentUnit().convert(10, "", "%")
        assert actual == 0.1
        actual = PercentUnit("%").convert(10, "")
        assert actual == 0.1

    def test_convert_show_suffix_param(self):
        actual = PercentUnit("%").convert(10, "", show_suffix=True)
        assert actual == "0.1"
        actual = PercentUnit().convert(0.1, "%", "", show_suffix=True)
        assert actual == "10.0%"

    def test_convert_decimal_param(self):
        actual = PercentUnit().convert(0.101, "%", "", decimal=1)
        assert actual == 10.1
        actual = PercentUnit().convert(0.101, "%", "", decimal=0)
        assert actual == 10.0
