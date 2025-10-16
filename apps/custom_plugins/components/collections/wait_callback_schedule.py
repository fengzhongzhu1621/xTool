from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service


class WaitCallbackService(Service):
    __need_schedule__ = True

    # 等待回调型的组件服务于周期轮询型的差异在于 interval 这个类属性，
    # 周期轮训型的服务该属性的值为间隔生成器，而回调型的服务该属性的值为 None。

    def _external_api_call(self):
        pass

    def execute(self, data, parent_data):
        """只做了一次 api 调用，然后就进入了等待回调的状态
        （如果在 execute() 方法中返回了 False，那么当前节点会进入 FAILED 状态，不会进入之后的等待回调阶段）
        """
        self._external_api_call()
        data.outputs.output_a = "output_a_value"
        return True

    def schedule(self, data, parent_data, callback_data=None):
        """检测第三方系统回调时传入的数据，来判断本次执行是否成功 ."""
        status = callback_data["status"]

        if status < 0:
            data.outputs.ex_data = "task failed with code: %s" % status
            return False

        data.outputs.status = status
        self.finish_schedule()


class WaitCallbackComponent(Component):
    name = "WaitCallbackComponent"
    code = "wait_callback_component"
    bound_service = WaitCallbackService
