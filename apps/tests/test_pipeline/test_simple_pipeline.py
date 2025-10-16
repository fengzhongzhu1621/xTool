import logging
import time

import pytest

pytestmark = pytest.mark.django_db

logging.basicConfig(level=logging.DEBUG)


@pytest.mark.skip
def test_run_pipeline():
    from bamboo_engine import api
    from bamboo_engine.builder import (
        EmptyEndEvent,
        EmptyStartEvent,
        ServiceActivity,
        builder,
    )
    from pipeline.eri.runtime import BambooDjangoRuntime

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
    """
    {
        'pd590cd86b071407c979799a40d11f0fe': {
            'archived_time': datetime.datetime(2023, 3, 13, 13, 56, 43, 756919),
            'children': {'e048141f07851405680607c9c9d922c3a': {
                'archived_time': datetime.datetime(2023, 3, 13, 13, 56, 43, 680624),
                'children': {},
                'created_time': datetime.datetime(2023, 3, 13, 13, 56, 43, 673556),
                'error_ignorable': False,
                'error_ignored': False,
                'id': 'e048141f07851405680607c9c9d922c3a',
                'loop': 1,
                'parent_id': 'pd590cd86b071407c979799a40d11f0fe',
                'retry': 0,
                'root_id:': 'pd590cd86b071407c979799a40d11f0fe',
                'skip': False,
                'started_time': datetime.datetime(2023, 3, 13, 13, 56, 43, 672706),
                'state': 'FINISHED',
                'version': 'v4421fb7f699446d79e7a65f25183c7f7'},
                         'e4252083ae1e34f048daf0b6cdefc666f': {
                             'archived_time': datetime.datetime(2023, 3, 13, 13, 56, 43, 749612),
                             'children': {},
                             'created_time': datetime.datetime(2023, 3, 13, 13, 56, 43, 734954),
                             'error_ignorable': False,
                             'error_ignored': False,
                             'id': 'e4252083ae1e34f048daf0b6cdefc666f',
                             'loop': 1,
                             'parent_id': 'pd590cd86b071407c979799a40d11f0fe',
                             'retry': 0,
                             'root_id:': 'pd590cd86b071407c979799a40d11f0fe',
                             'skip': False,
                             'started_time': datetime.datetime(2023, 3, 13, 13, 56, 43, 734566),
                             'state': 'FINISHED',
                             'version': 'v02e34ab5f7e744c993bcada7afa96ffe'},
                         'e4a4f975a615344589345d6c9de0a2287': {
                             'archived_time': datetime.datetime(2023, 3, 13, 13, 56, 43, 709687),
                             'children': {},
                             'created_time': datetime.datetime(2023, 3, 13, 13, 56, 43, 696731),
                             'error_ignorable': False,
                             'error_ignored': False,
                             'id': 'e4a4f975a615344589345d6c9de0a2287',
                             'loop': 1,
                             'parent_id': 'pd590cd86b071407c979799a40d11f0fe',
                             'retry': 0,
                             'root_id:': 'pd590cd86b071407c979799a40d11f0fe',
                             'skip': False,
                             'started_time': datetime.datetime(2023, 3, 13, 13, 56, 43, 696013),
                             'state': 'FINISHED',
                             'version': 'v799168664abf4b37b0883fae6ab49ce2'}},
            'created_time': datetime.datetime(2023, 3, 13, 13, 56, 43, 608447),
            'error_ignorable': False,
            'error_ignored': False,
            'id': 'pd590cd86b071407c979799a40d11f0fe',
            'loop': 1,
            'parent_id': 'pd590cd86b071407c979799a40d11f0fe',
            'retry': 0,
            'root_id:': 'pd590cd86b071407c979799a40d11f0fe',
            'skip': False,
            'started_time': datetime.datetime(2023, 3, 13, 13, 56, 43, 605775),
            'state': 'FINISHED',
            'version': 'vba0a6e9e32ad43a2a41c347639bc4d9f'}}
    """
