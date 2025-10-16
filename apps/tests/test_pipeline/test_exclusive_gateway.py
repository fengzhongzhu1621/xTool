import logging

import pytest

pytestmark = pytest.mark.django_db

logging.basicConfig(level=logging.DEBUG)


@pytest.mark.skip
def test_exclusive_gateway():
    from bamboo_engine import api
    from bamboo_engine.builder import (
        Data,
        EmptyEndEvent,
        EmptyStartEvent,
        ExclusiveGateway,
        NodeOutput,
        ServiceActivity,
        Var,
        build_tree,
    )
    from pipeline.eri.runtime import BambooDjangoRuntime

    start = EmptyStartEvent()
    act_1 = ServiceActivity(component_code="pipe_example_component", name="act_1")
    eg = ExclusiveGateway(
        conditions={0: "${act_1_output} < 0", 1: "${act_1_output} >= 0"},
        name="act_2 or act_3",
    )
    act_2 = ServiceActivity(component_code="pipe_example_component", name="act_2")
    act_3 = ServiceActivity(component_code="pipe_example_component", name="act_3")
    end = EmptyEndEvent()

    start.extend(act_1).extend(eg).connect(act_2, act_3).to(eg).converge(end)

    act_1.component.inputs.input_a = Var(type=Var.SPLICE, value="${input_a}")

    pipeline_data = Data()
    # 设置了一个值为 0 key 为 ${input_a} 的全局变量
    pipeline_data.inputs["${input_a}"] = Var(type=Var.PLAIN, value=0)
    # 声明了一个 key 为 ${act_1_output} 的全局变量，该变量是对 act_1 输出数据中 key 为 input_a 的变量的引用
    # source_act：要引用的变量所属的输出节点 ID
    # source_key：要引用的变量在其节点被输出后的 key
    pipeline_data.inputs["${act_1_output}"] = NodeOutput(type=Var.SPLICE, source_act=act_1.id, source_key="input_a")

    options = {
        "celery_disabled": True,
    }
    pipeline = build_tree(start, data=pipeline_data)

    api.run_pipeline(runtime=BambooDjangoRuntime(), pipeline=pipeline, **options)

    # 获取节点的执行结果
    result = api.get_execution_data_outputs(BambooDjangoRuntime(), act_1.id).data
    assert result["input_a"] == 0
