from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service


class WaitMultiCallbackService(Service):
    __need_schedule__ = True
    __multi_callback_enabled__ = True

    def _external_api_call(self):
        pass

    def execute(self, data, parent_data):
        self._external_api_call()
        data.outputs.output_a = "output_a_value"

        return True

    def schedule(self, data, parent_data, callback_data=None):
        status = callback_data["status"]

        if status < 0:
            data.outputs.ex_data = "task failed with code: %s" % status
            return False
        elif status < 1:
            data.outputs.status = status
            return True
        elif status > 999:
            raise Exception("status > 999")
        data.outputs.status = status

        self.finish_schedule()


class WaitMultiCallbackComponent(Component):
    name = "WaitMultiCallbackComponent"
    code = "wait_multi_callback_component"
    bound_service = WaitMultiCallbackService
