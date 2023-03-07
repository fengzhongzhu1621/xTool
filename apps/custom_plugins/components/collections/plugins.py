import math

from pipeline.component_framework.component import Component
from pipeline.core.flow.activity import Service


class FactorialCalculateService(Service):

    # data 是当前节点的数据对象，这个数据对象存储了用户传递给当前节点的参数的值以及当前节点输出的值
    # parent_data 则是该节点所属流程对象的数据对象，通常会将一些全局使用的常量存储在该对象中，如当前流程的执行者、流程的开始时间等。
    def execute(self, data, parent_data):
        n = data.get_one_of_inputs('n')
        if not isinstance(n, int):
            data.outputs.ex_data = 'n must be a integer!'
            return False

        data.outputs.factorial_of_n = math.factorial(n)
        return True

    def inputs_format(self):
        # 组件所需的输入字段，每个字段都包含字段名、字段键、字段类型及是否必填的说明。
        # 这个方法必须返回一个 InputItem 的数组，返回的这些信息能够用于确认某个组件需要获取什么样的输入数据。
        return [
            Service.InputItem(name='integer n', key='n', type='int', required=True)
        ]

    def outputs_format(self):
        # 组件执行成功时输出的字段，每个字段都包含字段名、字段键及字段类型的说明。
        # 这个方法必须返回一个 OutputItem 的数组，
        # 返回的这些信息能够用于确认某个组件在执行成功时输出的数据，便于在流程上下文或后续节点中进行引用。
        return [
            Service.OutputItem(name='factorial of n', key='factorial_of_n', type='int')
        ]


class FactorialCalculateComponent(Component):
    name = 'FactorialCalculateComponent'
    code = 'fac_cal_comp'
    bound_service = FactorialCalculateService
