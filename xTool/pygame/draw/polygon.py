import pygame

# 方向常量定义
DIR_UP = 1  # 向上
DIR_DOWN = 2  # 向下
DIR_LEFT = 3  # 向左
DIR_RIGHT = 4  # 向右


def draw_arrow(surf, color, posn, direction: int):
    """在指定表面上绘制箭头

    参数:
        surf: 目标表面
        color: 箭头颜色
        posn: 箭头中心位置 (x, y)
        direction: 箭头方向 (DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT)
    """
    x, y = posn
    # 根据方向定义箭头的四个顶点坐标
    if direction == DIR_UP:
        # 向上箭头：底部宽，顶部尖
        pointlist = ((x - 29, y + 30), (x + 30, y + 30), (x + 1, y - 29), (x, y - 29))
    elif direction == DIR_DOWN:
        # 向下箭头：顶部宽，底部尖
        pointlist = ((x - 29, y - 29), (x + 30, y - 29), (x + 1, y + 30), (x, y + 30))
    elif direction == DIR_LEFT:
        # 向左箭头：右侧宽，左侧尖
        pointlist = ((x + 30, y - 29), (x + 30, y + 30), (x - 29, y + 1), (x - 29, y))
    else:
        # 向右箭头：左侧宽，右侧尖
        pointlist = ((x - 29, y - 29), (x - 29, y + 30), (x + 30, y + 1), (x + 30, y))

    # 绘制多边形箭头
    _ = pygame.draw.polygon(surf, color, pointlist)
