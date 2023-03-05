import logging
import time

import pytest
from bamboo_engine import api
from bamboo_engine.builder import *

from pipeline.eri.runtime import BambooDjangoRuntime

# pytestmark = pytest.mark.django_db

logging.basicConfig(level=logging.DEBUG)


@pytest.mark.django_db
def test_run_pipeline():
    # 使用 builder 构造出流程描述结构
    start = EmptyStartEvent()
    # 这里先使用 bamboo-pipeline 自带的示例组件，我们会在后续的章节中学习如何自定义组件
    act = ServiceActivity(component_code="example_component")
    end = EmptyEndEvent()

    start.extend(act).extend(end)

    pipeline = builder.build_tree(start)

    # 执行流程对象
    runtime = BambooDjangoRuntime()

    api.run_pipeline(runtime=runtime, pipeline=pipeline)

    # 等待 1s 后获取流程执行结果
    time.sleep(1)

    result = api.get_pipeline_states(runtime=runtime, root_id=pipeline["id"])
    assert result
    print("*" * 100)
    print(result.data)


test_run_pipeline()
