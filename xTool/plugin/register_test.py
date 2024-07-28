from pydantic import BaseModel

from xTool.plugin.register import BaseInvocation, FunctionsManager, register_class, register_func


@register_func("add")
def add(x: int, y: int) -> int:
    return x + y


class Add(BaseInvocation):
    class Meta:
        func_name = "multiply"

    class Inputs(BaseModel):
        """
        输入校验器
        """

        x: int
        y: int

        class Meta:
            ordering = ["x", "y"]

    def invoke(self, x: int, y: int) -> int:
        return x * y


@register_class("subtract")
class Subtract:
    class Inputs(BaseModel):
        """
        输入校验器
        """

        x: int
        y: int

        class Meta:
            ordering = ["x", "y"]

    def __call__(self, x: int, y: int) -> int:
        return x - y


class TestFunctionsManager:
    def test_register_func(self):
        func = FunctionsManager.get_func("add")
        assert func(2, 3) == 5

    def test_register_class(self):
        func = FunctionsManager.get_func("subtract")
        assert func(2, 3) == -1

    def test_metaclass(self):
        func = FunctionsManager.get_func("multiply")
        assert func(2, 3) == 6
