# -*- coding: utf-8 -*-

import asyncio
import pytest
from xTool.tests.testing import loop_context


@pytest.fixture
def loop(loop_factory, fast, loop_debug):  # type: ignore
    """Return an instance of the event loop."""
    policy = loop_factory()
    asyncio.set_event_loop_policy(policy)
    with loop_context(fast=fast) as _loop:
        if loop_debug:
            _loop.set_debug(True)  # pragma: no cover
        asyncio.set_event_loop(_loop)
        yield _loop
