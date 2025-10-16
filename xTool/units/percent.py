from xTool.units.base import Unit


class PercentUnit(Unit):
    factor = 100
    suffixs = ["", "%"]
    template = "{value}{to_suffix}"
