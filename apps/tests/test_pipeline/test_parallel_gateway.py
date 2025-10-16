import logging

import pytest

pytestmark = pytest.mark.django_db

logging.basicConfig(level=logging.DEBUG)


@pytest.mark.skip
def test_parallel_gateway():
    from bamboo_engine import api
    from bamboo_engine.builder import (
        ConvergeGateway,
        EmptyEndEvent,
        EmptyStartEvent,
        ParallelGateway,
        ServiceActivity,
        build_tree,
    )
    from pipeline.eri.runtime import BambooDjangoRuntime

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
