import pytest

pytestmark = pytest.mark.django_db


@pytest.mark.skip
class TestFactorialCalculateComponent:

    def test_execute(self):
        from bamboo_engine import api, builder
        from bamboo_engine.builder import (
            Data,
            EmptyEndEvent,
            EmptyStartEvent,
            NodeOutput,
            ServiceActivity,
            Var,
        )
        from pipeline.eri.runtime import BambooDjangoRuntime

        # 使用 builder 构造出流程描述结构
        start = EmptyStartEvent()

        act_1 = ServiceActivity(component_code="fac_cal_comp")
        act_1.component.inputs.n = Var(type=Var.SPLICE, value="${input_a}")

        act_2 = ServiceActivity(component_code="fac_cal_comp")
        act_2.component.inputs.n = Var(type=Var.SPLICE, value="${act_1_output}")

        end = EmptyEndEvent()

        start.extend(act_1).extend(act_2).extend(end)

        # 设置全局变量
        pipeline_data = Data()
        pipeline_data.inputs["${input_a}"] = Var(type=Var.PLAIN, value=3)
        pipeline_data.inputs["${act_1_output}"] = NodeOutput(
            type=Var.SPLICE, source_act=act_1.id, source_key="factorial_of_n"
        )

        pipeline = builder.build_tree(start, data=pipeline_data)
        options = {
            "celery_disabled": True,
            "root_pipeline_data": {"a": 1},  # 可以从service.execute()中的parent_data获取到
        }
        api.run_pipeline(runtime=BambooDjangoRuntime(), pipeline=pipeline, **options)

        # 获取节点的执行结果
        result = api.get_execution_data_outputs(BambooDjangoRuntime(), act_1.id).data
        assert result["factorial_of_n"] == 6

        result = api.get_execution_data_outputs(BambooDjangoRuntime(), act_2.id).data
        assert result["factorial_of_n"] == 720
