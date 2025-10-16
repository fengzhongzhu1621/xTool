import json
import os
from typing import Any, List

from django.conf import settings


def format_serializer_data(serializer_data):
    return json.loads(json.dumps(serializer_data))


def assert_equal(actual, expect):
    """比较两个对象的值 ."""
    actual = format_serializer_data(actual)
    assert actual == expect


def assert_dict_contains(data: dict, expect: dict, key: str = None):
    """测试字典是否包含指定数据 ."""
    if not expect:
        try:
            assert data == expect
        except (AssertionError, AttributeError):
            print("-" * 100)
            print("key =", key, "actual =", data, "expect =", expect)
            print("-" * 100)
            raise
    for key, value in expect.items():
        if isinstance(value, dict):
            assert_dict_contains(data.get(key), value, key)
        elif isinstance(value, list):
            assert_list_contains(data.get(key), value, key)
        else:
            try:
                assert data.get(key) == value
            except (AssertionError, AttributeError):
                print("-" * 100)
                if data is None:
                    print("data = ", data, "key =", key, "expect =", value)
                else:
                    print("key =", key, "actual =", data.get(key), "expect =", value)
                print("-" * 100)
                raise


def assert_list_contains(data: list, expect: list, index: str = None):
    """测试数组是否包含指定数据 ."""
    if not expect:
        try:
            assert data == expect
        except (AssertionError, AttributeError):
            print("-" * 100)
            print("index =", index, "actual =", data, "expect =", expect)
            print("-" * 100)
            raise
    assert len(data) == len(expect)
    for index, value in enumerate(expect):
        if isinstance(value, dict):
            assert_dict_contains(data[index], value)
        elif isinstance(value, list):
            assert_list_contains(data[index], value, index)
        else:
            try:
                assert data[index] == value
            except AssertionError:
                print("-" * 100)
                print("index =", index, "actual =", data[index], "expect =", value)


def assert_response_base(rsp):
    """测试响应是否成功 ."""
    assert rsp.status_code == 200
    rsp_dict = rsp.json()
    assert rsp_dict["code"] == 0, f"response: {rsp_dict}"
    assert rsp_dict["result"]


def assert_error_code(rsp: Any, code: int):
    """测试响应是否失败，错误码是否符合预期 ."""
    assert rsp.status_code == 200
    rsp_dict = rsp.json()
    assert not rsp_dict["result"]
    assert rsp_dict["code"] == code, f"response: {rsp_dict}"


def assert_response(rsp, expect: Any):
    """测试响应是否成功，结果是否是字典且是否符合预期 ."""
    assert_response_base(rsp)
    if not isinstance(rsp.data, dict) or not isinstance(expect, dict):
        assert rsp.data == expect
        return
    assert_dict_contains(rsp.data, expect)


def assert_list_response(rsp, expect: List[dict]):
    """测试响应是否成功，结果是否是包含一个值的列表且是否符合预期 ."""
    assert_response_base(rsp)
    data = rsp.data
    assert data["page"] == 1
    assert data["total"] == len(expect)
    assert data["num_pages"] == 1
    assert_list_contains(data["results"], expect)


def add_pytest_fixture_plugins(path: str) -> List[str]:
    """添加额外的 fixtures"""

    def refactor(string: str) -> str:
        return string.strip("/").strip("\\").replace("/", ".").replace("\\", ".").replace(".py", "")

    prefix = settings.BASE_DIR
    prefix_len = len(prefix)
    paths = []
    for dir_path, _, filenames in os.walk(path):
        for filename in filenames:
            if filename.startswith("__"):
                continue
            if not filename.endswith(".py"):
                continue
            full_path = os.path.join(dir_path, filename)
            paths.append(refactor(full_path[prefix_len:]))

    return paths
