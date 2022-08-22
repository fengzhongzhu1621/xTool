# -*- coding: utf-8 -*-

from typing import Union
from xTool.units.exceptions import UnitSuffixNotFound


class Unit:

    def __init__(self, suffix: str = "") -> None:
        self.suffix = suffix

    def convert(self,
                value: Union[int, float],
                to_suffix: str,
                from_suffix: str = "",
                decimal=None,
                show_suffix=False) -> Union[int, float, str]:
        if from_suffix == "":
            from_suffix = self.suffix
        try:
            from_suffix_index = self.suffixs.index(from_suffix)
        except ValueError:
            raise UnitSuffixNotFound(suffix=from_suffix)
        try:
            to_suffix_index = self.suffixs.index(to_suffix)
        except ValueError:
            raise UnitSuffixNotFound(suffix=to_suffix)
        if from_suffix == to_suffix:
            return value
        distance = to_suffix_index - from_suffix_index
        if distance > 0:
            value = value * (self.factor**distance)
        elif distance < 0:
            value = value / (self.factor**(distance * -1))

        if decimal is not None:
            value = round(value, decimal)

        if show_suffix:
            value = self.template.format(
                **{
                    "value": value,
                    "from_suffix": from_suffix,
                    "to_suffix": to_suffix,
                })
        return value
