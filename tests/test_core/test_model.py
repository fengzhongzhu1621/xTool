from core.models import get_custom_app_models, get_model_from_app


def test_get_model_from_app():
    app_info = get_model_from_app("apps.global_conf")
    actual = {app["model"] for app in app_info}
    expect = {"GlobalConfig", "SystemConfig", "Dictionary"}
    assert actual == expect


def test_get_custom_app_models():
    app_info_list = get_custom_app_models()
    actual = {app["model"] for app in app_info_list}
    expect = {
        "ApiWhiteList",
        "Area",
        "Credential",
        "CredentialResource",
        "Data",
        "Dept",
        "Dictionary",
        "FieldPermission",
        "GlobalConfig",
        "LoginLog",
        "Menu",
        "MenuButton",
        "MenuField",
        "MessageCenter",
        "MessageCenterTargetUser",
        "OperationLog",
        "Post",
        "RequestApiConfig",
        "RequestSystemConfig",
        "Role",
        "RoleMenuButtonPermission",
        "RoleMenuPermission",
        "SystemConfig",
        "Users",
        "VersionLogVisited",
    }
    assert actual == expect
