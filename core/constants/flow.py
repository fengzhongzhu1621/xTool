from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _lazy

FIELD_VIEW_TYPE_STRING = "STRING"


class NodeType(TextChoices):
    """流程节点 ."""

    START_STATE = "START", _lazy("开始节点")
    NORMAL_STATE = "NORMAL", _lazy("普通节点")
    SIGN_STATE = "SIGN", _lazy("会签节点")
    APPROVAL_STATE = "APPROVAL", _lazy("审批节点")
    TASK_STATE = "TASK", _lazy("自动节点")
    TASK_SOPS_STATE = "TASK-SOPS", _lazy("标准运维节点")
    TASK_DEVOPS_STATE = "TASK-DEVOPS", _lazy("蓝盾任务节点")
    ROUTER_STATE = "ROUTER", _lazy("分支网关节点")
    ROUTER_P_STATE = "ROUTER-P", _lazy("并行网关节点")
    COVERAGE_STATE = "COVERAGE", _lazy("汇聚网关节点")
    END_STATE = "END", _lazy("结束节点")
    VIRTUAL_STATE = "MIGRATE", _lazy("VIRTUAL_STATE")
    WEBHOOK_STATE = "WEBHOOK", _lazy("WebHook节点")
    BK_PLUGIN_STATE = "BK-PLUGIN", _lazy("BK-蓝鲸插件节点")


SOURCE_CHOICES = [
    ("EMPTY", _lazy("无")),
    ("CUSTOM", _lazy("自定义数据")),
    ("API", _lazy("接口数据")),
    ("DATADICT", _lazy("数据字典")),
    ("RPC", _lazy("系统数据")),
    ("CUSTOM_API", _lazy("自定义API")),
]


class FieldViewType(TextChoices):
    STRING = "STRING", _lazy("单行文本")
    TEXT = "TEXT", _lazy("多行文本")
    RICHTEXT = "RICHTEXT", _lazy("富文本")
    INT = "INT", _lazy("数字")
    SELECT = "SELECT", _lazy("单选下拉框")
    INPUTSELECT = "INPUTSELECT", _lazy("可输入单选下拉框")
    MULTISELECT = "MULTISELECT", _lazy("多选下拉框")
    LINK = "LINK", _lazy("链接")
    DATE = "DATE", _lazy("日期")
    DATETIME = "DATETIME", _lazy("时间")
    DATETIMERANGE = "DATETIMERANGE", _lazy("时间间隔")
    RADIO = "RADIO", _lazy("单选框")
    SWITCH = "SWITCH", _lazy("开关")
    RADIO_GROUP = "RADIO_GROUP", _lazy("单选框组")
    MEMBER = "MEMBER", _lazy("单选人员选择")
    MEMBERS = "MEMBERS", _lazy("多选人员选择")
    FIELD_TABLE = "FIELD_TABLE", _lazy("字段配置表格")
    PANEL = "PANEL", _lazy("面板")
    CHECKBOX = "CHECKBOX", _lazy("复选框")
    NUMBER = "NUMBER", _lazy("数字框")


class FieldValidateType(TextChoices):
    """字段验证类型 ."""

    OPTION = "OPTION", _lazy("选填")
    REQUIRE = "REQUIRE", _lazy("必填")


FIELD_STORAGE_TYPE_CHOICES = [
    ("string", _lazy("string")),
    ("int", _lazy("int")),
    ("object", _lazy("object")),
    ("timestamp", _lazy("timestamp")),
]
