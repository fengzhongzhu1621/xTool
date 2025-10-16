"""
__set_name__ 方法是 Python 3.6 中引入的一种特殊方法，它可以在类属性被赋值时自动调用。
这个方法可以用来处理类属性的名称绑定问题，例如将类属性与其所在的类进行绑定。

具体来说，当一个类定义了一个描述符（descriptor）并将其作为类属性时，Python 将在该类定义完成后自动调用描述符的 __set_name__ 方法，
并将该类属性的名称作为参数传递给该方法。这样，我们就可以在 __set_name__ 方法中访问该类属性的名称，并将其与描述符进行绑定。

注意事项
1. __set_name__ 只在描述符被用作类属性时调用
2. 如果描述符实例已经通过参数提供了 name，通常不需要 __set_name__
3. 在多重继承场景下，描述符的 __set_name__ 只会被调用一次
"""


class Descriptor:
    """描述符类"""

    def __set_name__(self, owner, name):
        self.name = name
        print(f"Descriptor.__set_name__(owner={owner}, name={name})")

    def __get__(self, instance, owner):
        print(f"Descriptor.__get__(instance={instance}, owner={owner})")
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        # Descriptor.__set__(instance=<xTool.descriptor.set_name_test.MyClass object at 0x11c5e1a10>, value=attr value)
        print(f"Descriptor.__set__(instance={instance}, value={value})")
        instance.__dict__[self.name] = value


class MyClass:
    # 将 Descriptor 实例作为其类属性 my_attr 的值
    # 当 Python 解释器执行到 MyClass 类定义结束时，它会自动调用 Descriptor.__set_name__() 方法，
    # 并将 MyClass 类和属性名 my_attr 作为参数传递给该方法。
    #
    # 当创建 MyClass 实例并访问其 my_attr 属性时，Python 将自动调用描述符的 __get__ 和 __set__ 方法，
    # 并分别输出相应的消息以演示这些方法的调用时机。
    my_attr = Descriptor()


def test__set_name__():
    obj = MyClass()
    obj.my_attr = "attr value"


class DocumentedProperty:
    def __init__(self, doc=None):
        self.doc = doc

    def __set_name__(self, owner, name):
        if self.doc is None:
            self.doc = f"Property {name} documentation"

    def __get__(self, instance, owner):
        return self.doc


class MyClass2:
    """自动生成文档字符串 ."""

    prop = DocumentedProperty()

    def __init__(self):
        print(self.prop)  # 输出: Property prop documentation


def test__set_name__2():
    MyClass2()


class Registry:
    _registry = {}

    def __set_name__(self, owner, name):
        self._registry[owner.__name__] = name


class MyClass3:
    attr = Registry()


def test__set_name__3():
    print(Registry._registry)  # {'MyClass3': 'attr'}
