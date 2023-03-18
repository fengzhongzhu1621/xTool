import logging

import pytest
from bamboo_engine import api
from bamboo_engine.builder import *

from pipeline.eri.runtime import BambooDjangoRuntime

pytestmark = pytest.mark.django_db

logging.basicConfig(level=logging.DEBUG)


def test_schedule_component():
    # 使用 builder 构造出流程描述结构
    start = EmptyStartEvent()
    act = ServiceActivity(component_code="schedule_component")
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
