from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service, StaticIntervalGenerator


class ScheduleService(Service):
    """
    周期性轮询：完成 execute() 的执行后，还会周期性的执行 schedule() 方法，直至满足一定的条件为止。

    如果我们需要周期性的轮询第三方平台的接口，那么可以使用周期性轮询的执行方式，下面的代码定义了一个周期性轮询的组件服务：

    一个周期性轮询组件服务必须包含两个类属性：

    __need_schedule__： 表示当前组件服务是否需要调度，周期性轮询的方式下必须将该字段设置为 True
    interval：轮询间隔生成器，周期性轮询方式下该字段必须为 AbstractIntervalGenerator 的子类。

    """
    __need_schedule__ = True
    interval = StaticIntervalGenerator(2)

    def __init__(self, *args, **kwargs):
        self.status = 2

    def _get_poll_url(self):
        pass

    def _poll_status(self, poll_url):
        self.status -= 1
        return self.status

    def execute(self, data, parent_data):
        """
        调用第三方系统获取了用于轮询的 poll_url，并将其写入到输出中（如果在 execute() 方法中返回了 False，
        那么当前节点会进入 FAILED 状态，不会进入之后的轮询阶段

        :param data:
        :param parent_data:
        :return:
        """
        poll_url = self._get_poll_url()
        data.outputs.poll_url = poll_url
        return True

    def schedule(self, data, parent_data, callback_data=None):
        """
        使用在 execute() 中设置到输出中的 poll_url 来轮询第三方系统的状态，并根据其返回值来决定该次轮询的结果


        :param data: 当前节点的数据对象，这个数据对象存储了用户传递给当前节点的参数的值以及当前节点输出的值。
        :param parent_data: 该节点所属流程对象的数据对象。
        :param callback_data: 回调数据，在等待回调模式下由第三方系统传入的数据。
        :return: True：当次轮询成功，若轮询已完成则节点会进入 FINISHED 状态，否则仍然处于 RUNNING 状态，等待进入下次轮询。
                 False：当次轮询失败，节点会进入 FAILED 状态。
        """
        poll_url = data.get_one_of_outputs('poll_url')
        status = self._poll_status(poll_url)

        if status == 0:
            # 轮询已完成, 可调用 finish_schedule() 方法，则节点会进入 FINISHED 状态
            self.finish_schedule()
        elif status < 0:
            data.outputs.ex_data = 'task failed with code: %s' % status
            return False
        else:
            # 不符合条件，则仍然处于 RUNNING 状态，等待进入下次轮询。
            pass
        return True


class ScheduleComponent(Component):
    name = 'ScheduleComponent'
    code = 'schedule_component'
    bound_service = ScheduleService
