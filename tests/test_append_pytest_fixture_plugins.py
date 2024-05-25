from pathlib import Path

from xTool.testing.pytest_plugin import append_pytest_fixture_plugins


def test_append_pytest_fixture_plugins():
    path = Path(__file__).parent / "fixtures"
    root_path = Path(__file__).parent.parent
    actual = append_pytest_fixture_plugins(root_path, path)
    expect = [
        "tests.fixtures.thread",
        "tests.fixtures.signal",
        "tests.fixtures.net",
        "tests.fixtures.request",
        "tests.fixtures.cache",
        "tests.fixtures.loop",
    ]
    assert actual == expect
