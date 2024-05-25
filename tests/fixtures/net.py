import pytest


@pytest.fixture
def aiomisc_unused_port():
    from xTool.net.utils import get_unused_port

    return get_unused_port()
