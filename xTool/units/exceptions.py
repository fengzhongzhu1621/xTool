from xTool.exceptions import XToolException


class UnitException(XToolException):
    pass


class UnitSuffixNotFound(UnitException):

    def __init__(self, suffix=None, *args, **kwargs):
        self.suffix = suffix
        super().__init__(*args, **kwargs)
