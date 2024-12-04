import pytest

from xTool import exceptions


class SanicExceptionTestException(Exception):
    pass


def test_XToolConfigException():
    with pytest.raises(exceptions.XToolConfigException):
        raise exceptions.XToolConfigException


def test_XToolSensorTimeout():
    with pytest.raises(exceptions.XToolSensorTimeout):
        raise exceptions.XToolSensorTimeout


def test_XToolTaskTimeout():
    with pytest.raises(exceptions.XToolTaskTimeout):
        raise exceptions.XToolTaskTimeout


def test_XToolWebServerTimeout():
    with pytest.raises(exceptions.XToolWebServerTimeout):
        raise exceptions.XToolWebServerTimeout


def test_XToolSkipException():
    with pytest.raises(exceptions.XToolSkipException):
        raise exceptions.XToolSkipException


def test_XToolDagCycleException():
    with pytest.raises(exceptions.XToolDagCycleException):
        raise exceptions.XToolDagCycleException


def divide(a: int, b: int) -> float:
    return a / b


def test_better_exceptions():
    divide(10, 0)
