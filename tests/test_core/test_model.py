from core.models import get_model_from_app


def test_get_model_from_app():
    app_info = get_model_from_app("apps.global_conf")
    actual = set(app["model"] for app in app_info)
    expect = {"GlobalConfig", "SystemConfig", "Dictionary"}
    assert actual == expect
