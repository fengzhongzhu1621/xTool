class MakoSandboxEscapeException(Exception):
    pass


class NotMakoTemplateException(MakoSandboxEscapeException):
    pass


class ForbiddenMakoTemplateException(MakoSandboxEscapeException):
    pass


class ForbiddenExtractNodeException(ForbiddenMakoTemplateException):
    pass


class MakoResultIsNotBoolTypeException(Exception):
    pass
