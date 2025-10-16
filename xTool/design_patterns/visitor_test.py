from typing import List

from visitor import Visitor

########################################################################################################################
# 定义 Elements


class Shape:
    def accept(self, visitor: Visitor):
        # 执行访问者对当前对象的扩展操作
        visitor.visit(self)


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height


########################################################################################################################
# 定义 Visitor，用于扩展了 Element 的方法，将Element 的方法和属性分离


class ShapeVisitor(Visitor):
    def visit_Circle(self, circle):
        print("绘制圆形")

    def visit_Rectangle(self, rectangle):
        print("绘制正方形")


class Canvas(Shape):
    def __init__(self, shapes: List[Shape]):
        self.shapes = shapes


class ShapeNestedVisitor(Visitor):
    def visit_Circle(self, circle):
        print("绘制圆形")

    def visit_Rectangle(self, rectangle):
        print("绘制正方形")

    def visit_Canvas(self, canvas):
        print("绘制 cavas")
        for shape in canvas.shapes:
            shape.accept(self)


class AreaCalculator(Visitor):
    def visit_Circle(self, circle):
        area = 3.1415926 * (circle.radius**2)
        print(f'计算圆形的面积: {area}')

    def visit_Rectangle(self, rectangle):
        area = rectangle.width * rectangle.height
        print(f'计算长方形的面积: {area}')


def test_shape_visitor():
    shapes = [Circle(1), Rectangle(2, 3)]
    visitor = ShapeVisitor()
    for shape in shapes:
        shape.accept(visitor)


def test_shape_nested_visitor():
    """元素嵌套 ."""
    shapes = Canvas([Circle(1), Rectangle(2, 3)])
    visitor = ShapeNestedVisitor()
    shapes.accept(visitor)


def test_area():
    shapes = [Circle(1), Rectangle(2, 3)]
    visitor = ShapeVisitor()
    for shape in shapes:
        shape.accept(visitor)
