import pytest
from django.conf import settings


def pytest_configure():
    """
    pytest_configure 是一个 pytest 插件生命周期钩子（hook），在 pytest 配置阶段被调用。
    这个钩子允许你在 pytest 开始运行之前自定义配置，
    例如注册自定义标记（markers）、插件或自定义测试失败的报告。
    """
    settings.configure(
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3"}},
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.admin",
            "apps.websocket",
        ],
        SECRET_KEY="Not_a_secret_key",
    )


def pytest_generate_tests(metafunc):
    """
    pytest_generate_tests 是一个 pytest 插件生命周期钩子（hook），用于动态生成测试用例。
    这个钩子允许你根据参数化的数据自动生成测试函数，而无需手动为每个测试用例编写单独的测试函数。

    通过使用 pytest_generate_tests 钩子，你可以动态生成测试用例，从而简化测试代码并提高代码复用率。
    这在处理具有相似结构的测试用例时非常有用。
    """
    if "samesite" in metafunc.fixturenames:
        # 当你需要将某些参数传递给测试函数，但这些参数本身是由其他 fixture 提供的时，可以使用 indirect 参数。
        # indirect 参数允许你将一个或多个参数标记为间接参数。
        # 这意味着这些参数将由相应的 fixture 函数提供，而不是直接从 parametrize 装饰器中获取。
        metafunc.parametrize("samesite", ["Strict", "None"], indirect=True)


@pytest.fixture
def samesite(request, settings):
    """Set samesite flag to strict."""
    settings.SESSION_COOKIE_SAMESITE = request.param


@pytest.fixture
def samesite_invalid(settings):
    """Set samesite flag to strict."""
    settings.SESSION_COOKIE_SAMESITE = "Hello"
