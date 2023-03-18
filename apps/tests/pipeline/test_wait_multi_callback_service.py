import logging

import pytest
from bamboo_engine import api
from bamboo_engine.builder import *

from pipeline.eri.runtime import BambooDjangoRuntime

pytestmark = pytest.mark.django_db

logging.basicConfig(level=logging.DEBUG)


def test_wait_multi_callback_schedule_component__schedule_success():
    # 使用 builder 构造出流程描述结构
    start = EmptyStartEvent()
    # 这里先使用 bamboo-pipeline 自带的示例组件，我们会在后续的章节中学习如何自定义组件
    act = ServiceActivity(component_code="wait_multi_callback_component")
    end = EmptyEndEvent()

    # 将节点连接
    start.extend(act).extend(end)

    # 构造一个节点树，start是根节点
    pipeline = builder.build_tree(start)

    # 创建运行时
    runtime = BambooDjangoRuntime()

    # 执行流程
    options = {
        "celery_disabled": True,
    }
    api.run_pipeline(runtime=runtime, pipeline=pipeline, **options)

    # 获得节点的版本
    state = runtime.get_state(act.id)
    version = state.version

    # 执行指定节点的回调，执行成功后继续执行流程的下一个节点
    result = api.callback(runtime, act.id, version=version, data={"status": 1})
    assert result.result is True

    # 成功后再次执行，则当前节点的进程不是休眠状态，不能执行
    result = api.callback(runtime, act.id, version=version, data={"status": 2})
    assert result.result is False


def test_wait_multi_callback_schedule_component__schedule_failure():
    # 使用 builder 构造出流程描述结构
    start = EmptyStartEvent()
    # 这里先使用 bamboo-pipeline 自带的示例组件，我们会在后续的章节中学习如何自定义组件
    act = ServiceActivity(component_code="wait_multi_callback_component")
    end = EmptyEndEvent()

    # 将节点连接
    start.extend(act).extend(end)

    # 构造一个节点树，start是根节点
    pipeline = builder.build_tree(start)

    # 创建运行时
    runtime = BambooDjangoRuntime()

    # 执行流程
    options = {
        "celery_disabled": True,
    }
    api.run_pipeline(runtime=runtime, pipeline=pipeline, **options)

    # 获得节点的版本
    state = runtime.get_state(act.id)
    version = state.version

    # 第一次schedule执行失败
    result = api.callback(runtime, act.id, version=version, data={"status": -1})
    assert result.result is True

    # 第一次执行是需要判断节点的状态，不为RUNNING则停止执行
    result = api.callback(runtime, act.id, version=version, data={"status": 1})
    assert result.result is True


def test_wait_multi_callback_schedule_component__schedule_repeat():
    # 使用 builder 构造出流程描述结构
    start = EmptyStartEvent()
    act = ServiceActivity(component_code="wait_multi_callback_component")
    end = EmptyEndEvent()

    # 将节点连接
    start.extend(act).extend(end)

    # 构造一个节点树，start是根节点
    pipeline = builder.build_tree(start)

    # 创建运行时
    runtime = BambooDjangoRuntime()

    # 执行流程
    options = {
        "celery_disabled": True,
    }
    api.run_pipeline(runtime=runtime, pipeline=pipeline, **options)

    # 获得节点的版本
    state = runtime.get_state(act.id)
    version = state.version

    # 第一次schedule执行，流程暂停
    result = api.callback(runtime, act.id, version=version, data={"status": 0})
    assert result.result is True
    result = api.get_execution_data_outputs(runtime, act.id)
    assert result.data == {'output_a': 'output_a_value', '_result': True, '_loop': 1, '_inner_loop': 1, 'status': 0}

    # 再次执行，重新执行该节点的schedule逻辑
    result = api.callback(runtime, act.id, version=version, data={"status": 1})
    assert result.result is True
    result = api.get_execution_data_outputs(runtime, act.id)
    assert result.data == {'output_a': 'output_a_value', '_result': True, '_loop': 1, '_inner_loop': 1, 'status': 1}


def test_wait_multi_callback_schedule_component__schedule_exception_repeat():
    # 使用 builder 构造出流程描述结构
    start = EmptyStartEvent()
    act = ServiceActivity(component_code="wait_multi_callback_component")
    end = EmptyEndEvent()

    # 将节点连接
    start.extend(act).extend(end)

    # 构造一个节点树，start是根节点
    pipeline = builder.build_tree(start)

    # 创建运行时
    runtime = BambooDjangoRuntime()

    # 执行流程
    options = {
        "celery_disabled": True,
    }
    api.run_pipeline(runtime=runtime, pipeline=pipeline, **options)

    # 获得节点的版本
    state = runtime.get_state(act.id)
    version = state.version

    # 第一次schedule执行，抛出异常，节点状态标记为失败，流程暂停
    result = api.callback(runtime, act.id, version=version, data={"status": 1000})
    assert result.result is True
    result = api.get_execution_data_outputs(runtime, act.id)
    assert result.result is True
    assert result.data["output_a"] == "output_a_value"
    assert result.data["_result"] is False

    # 触发失败节点重试
    result = api.retry_node(runtime, act.id, data={})
    assert result.result is True
    result = api.get_execution_data_outputs(runtime, act.id)
    assert result.data == {'output_a': 'output_a_value', '_result': True, '_loop': 1, '_inner_loop': 1}

    # 需要重新获得节点的版本
    state = runtime.get_state(act.id)
    version = state.version

    # 第二次schedule执行，执行成功
    result = api.callback(runtime, act.id, version=version, data={"status": 2})
    assert result.result is True
    result = api.get_execution_data_outputs(runtime, act.id)
    assert result.data == {'output_a': 'output_a_value', '_result': True, '_loop': 1, '_inner_loop': 1, 'status': 2}
