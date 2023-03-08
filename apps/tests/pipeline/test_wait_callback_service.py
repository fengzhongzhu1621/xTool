import logging

import pytest
from bamboo_engine import api
from bamboo_engine.builder import *

from pipeline.eri.runtime import BambooDjangoRuntime

pytestmark = pytest.mark.django_db

logging.basicConfig(level=logging.DEBUG)


def test_wait_callback_schedule_component():
    # 使用 builder 构造出流程描述结构
    start = EmptyStartEvent()
    # 这里先使用 bamboo-pipeline 自带的示例组件，我们会在后续的章节中学习如何自定义组件
    act = ServiceActivity(component_code="wait_callback_component")
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

    # 执行指定节点的回调，执行完后继续执行流程的下一个节点
    api.callback(runtime, act.id, version=version, data={"status": 1})
