import logging
import time

import pytest
from bamboo_engine import api
from bamboo_engine.builder import *

from pipeline.eri.runtime import BambooDjangoRuntime

# pytestmark = pytest.mark.django_db

logging.basicConfig(level=logging.DEBUG)


@pytest.mark.django_db()
def test_run_pipeline():
    # 使用 builder 构造出流程描述结构
    start = EmptyStartEvent()
    # 这里先使用 bamboo-pipeline 自带的示例组件，我们会在后续的章节中学习如何自定义组件
    act = ServiceActivity(component_code="example_component")
    end = EmptyEndEvent()

    # 将节点连接
    start.extend(act).extend(end)

    # 构造一个节点树，start是根节点
    pipeline = {
        "id": "p745f86676a4c451e833ae0300f75fb76",
        "start_event": {
            "incoming": "",
            "outgoing": "fa7a07296e19e405bbb1f697f50e40891",
            "type": "EmptyStartEvent",
            "id": "ef2ba007a736643d5af0a28d8b9e9dcf9",
            "name": None,
        },
        "end_event": {
            "incoming": ["fe174ecdf64244a0ebf23ea858f5c4a0d"],
            "outgoing": "",
            "type": "EmptyEndEvent",
            "id": "e5bc1f6eb996f49ea9ac7edbedeec1790",
            "name": None,
        },
        "activities": {
            "eb34435bd8995435eb3a8ba945b221b64": {
                "incoming": ["fa7a07296e19e405bbb1f697f50e40891"],
                "outgoing": "fe174ecdf64244a0ebf23ea858f5c4a0d",
                "type": "ServiceActivity",
                "id": "eb34435bd8995435eb3a8ba945b221b64",
                "name": None,
                "error_ignorable": False,
                "timeout": None,
                "skippable": True,
                "retryable": True,
                "component": {"code": "example_component", "inputs": {}},
                "optional": False,
            }
        },
        "gateways": {},
        "flows": {
            "fa7a07296e19e405bbb1f697f50e40891": {
                "is_default": False,
                "source": "ef2ba007a736643d5af0a28d8b9e9dcf9",
                "target": "eb34435bd8995435eb3a8ba945b221b64",
                "id": "fa7a07296e19e405bbb1f697f50e40891",
            },
            "fe174ecdf64244a0ebf23ea858f5c4a0d": {
                "is_default": False,
                "source": "eb34435bd8995435eb3a8ba945b221b64",
                "target": "e5bc1f6eb996f49ea9ac7edbedeec1790",
                "id": "fe174ecdf64244a0ebf23ea858f5c4a0d",
            },
        },
        "data": {"inputs": {}, "outputs": []},  # 流程的输入参数
    }
    pipeline = builder.build_tree(start)

    # 创建运行时
    runtime = BambooDjangoRuntime()

    # 执行流程
    options = {
        "cycle_tolerate": False,  # 默认无环
        "queue": "",
        "priority": 100,
        "celery_disabled": True,
    }
    api.run_pipeline(runtime=runtime, pipeline=pipeline, **options)

    # 等待 1s 后获取流程执行结果
    time.sleep(1)

    # 获得流程执行结果
    result = api.get_pipeline_states(runtime=runtime, root_id=pipeline["id"])
    assert result.data
