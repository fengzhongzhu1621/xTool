from typing import Any


def check_circle(mouse_pos_x, mouse_pos_y, center_x, center_y, radius) -> Any:
    """一个几何距离检测函数，用于判断鼠标坐标是否在指定圆内：

    数学原理
        使用圆的方程 (x - center_x)² + (y - center_y)² < radius²

    返回值

        True：如果鼠标在圆内（距离小于半径）
        False：如果鼠标在圆外（距离大于等于半径）
    """
    return (mouse_pos_x - center_x) ** 2 + (mouse_pos_y - center_y) ** 2 < radius**2
