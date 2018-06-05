#coding: utf-8

import pytest

from xTool import exceptions


def test_XToolConfigException():
    with pytest.raises(exceptions.XToolConfigException) as excinfo:
        raise exceptions.XToolConfigException


def test_XToolSensorTimeout():
    with pytest.raises(exceptions.XToolSensorTimeout) as excinfo:
        raise exceptions.XToolSensorTimeout


def test_XToolTaskTimeout():
    with pytest.raises(exceptions.XToolTaskTimeout) as excinfo:
        raise exceptions.XToolTaskTimeout


def test_XToolWebServerTimeout():
    with pytest.raises(exceptions.XToolWebServerTimeout) as excinfo:
        raise exceptions.XToolWebServerTimeout


def test_XToolSkipException():
    with pytest.raises(exceptions.XToolSkipException) as excinfo:
        raise exceptions.XToolSkipException


def test_XToolDagCycleException():
    with pytest.raises(exceptions.XToolDagCycleException) as excinfo:
        raise exceptions.XToolDagCycleException

