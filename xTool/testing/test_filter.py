from xTool.design_patterns.filter.chain import AfterFilter, BeforeFilter, Method
from xTool.plugin import PluginType, register_plugin


class Context:
    def __init__(self):
        self.value = []


class BusinessMethod(Method):
    def process_direct(self, context):
        context.value.append(2)
        return context

    async def async_process_direct(self, context):
        context.value.append(22)
        return context


@register_plugin(PluginType.BEFORE_FILTER, "test")
class BusinessBeforeFilter(BeforeFilter):
    def before_process(self, context):
        context.value.append(1)

    async def async_before_process(self, context):
        context.value.append(11)


@register_plugin(PluginType.AFTER_FILTER, "test")
class BusinessAfterFilter(AfterFilter):
    def after_process(self, context):
        context.value.append(3)

    async def async_after_process(self, context):
        context.value.append(33)
