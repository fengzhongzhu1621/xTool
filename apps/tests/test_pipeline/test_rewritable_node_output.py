import logging

import pytest

pytestmark = pytest.mark.django_db

logging.basicConfig(level=logging.DEBUG)


@pytest.mark.skip
def test_rewritable_node_output():
    """
    RewritableNodeOutput 能够帮助我们在数据上下文中声明一个引用多个节点输出的变量，这个变量值会在其引用的节点执行完后进行刷新
    """
    from bamboo_engine import api
    from bamboo_engine.builder import (
        Data,
        EmptyEndEvent,
        EmptyStartEvent,
        RewritableNodeOutput,
        ServiceActivity,
        Var,
        build_tree,
    )
    from pipeline.eri.runtime import BambooDjangoRuntime

    start = EmptyStartEvent()
    act_1 = ServiceActivity(component_code="debug_node")
    act_1.component.inputs.param_1 = Var(type=Var.PLAIN, value="output_value_1")
    act_2 = ServiceActivity(component_code="debug_node")
    act_2.component.inputs.context_var = Var(type=Var.SPLICE, value="${rewritable_output}")
    act_2.component.inputs.param_2 = Var(type=Var.PLAIN, value="output_value_2")
    act_3 = ServiceActivity(component_code="debug_node")
    act_3.component.inputs.context_var = Var(type=Var.SPLICE, value="${rewritable_output}")
    end = EmptyEndEvent()

    start.extend(act_1).extend(act_2).extend(act_3).extend(end)

    pipeline_data = Data()
    # 数据上下文的 ${rewritable_output} 变量引用了来自 act_1 及 act_2 两个节点的输出字段，
    # 当 act_1 执行完成时，${rewritable_output} 的值为 output_value_1，act_2 中 context_var 解析后的值为 output_value_1，
    # 当 act_2 执行完成后，${rewritable_output} 的值为 output_value_2，act_3 中 context_var 解析后的值为 output_value2。
    pipeline_data.inputs["${rewritable_output}"] = RewritableNodeOutput(
        source_act=[
            {"source_act": act_1.id, "source_key": "param_1"},
            {"source_act": act_2.id, "source_key": "param_2"},
        ],
        type=Var.SPLICE,
        value="",
    )

    pipeline = build_tree(start, data=pipeline_data)
    # 创建运行时
    runtime = BambooDjangoRuntime()

    # 执行流程
    options = {
        "celery_disabled": True,
    }
    api.run_pipeline(runtime=runtime, pipeline=pipeline, **options)
