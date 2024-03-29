import logging

import pytest
from bamboo_engine import api
from bamboo_engine.builder import (
    build_tree,
    EmptyStartEvent,
    ServiceActivity,
    EmptyEndEvent,
    ParallelGateway,
    ConvergeGateway,
)

from pipeline.eri.runtime import BambooDjangoRuntime

pytestmark = pytest.mark.django_db

logging.basicConfig(level=logging.DEBUG)


def test_parallel_gateway():
    start = EmptyStartEvent()
    pg = ParallelGateway()
    act_1 = ServiceActivity(component_code="pipe_example_component", name="act_1")
    act_2 = ServiceActivity(component_code="pipe_example_component", name="act_2")
    act_3 = ServiceActivity(component_code="pipe_example_component", name="act_3")
    cg = ConvergeGateway()
    end = EmptyEndEvent()

    start.extend(pg).connect(act_1, act_2, act_3).to(pg).converge(cg).extend(end)

    pipeline = build_tree(start)
    api.run_pipeline(runtime=BambooDjangoRuntime(), pipeline=pipeline)
