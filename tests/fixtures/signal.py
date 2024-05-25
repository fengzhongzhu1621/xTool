import pytest

from xTool.decorators.signal import Signal


@pytest.fixture
def signal():
    return Signal()
