"""pg.examples.stars

    我们都身处阴沟，但仍有人仰望星空。
    We are all in the gutter,
    but some of us are looking at the stars.
                                            -- Oscar Wilde

一个简单的星空场示例。注意你可以通过左键点击窗口来移动星空场的"中心"。
A simple starfield example. Note you can move the 'center' of
the starfield by leftclicking in the window. This example show
the basics of creating a window, simple pixel plotting, and input
event management.

这个示例展示了创建窗口、简单像素绘制和输入事件管理的基础知识。
"""

import math
import random

import pygame as pg

# 常量定义
# constants
WINSIZE = [640, 480]  # 窗口尺寸：640x480像素
WINCENTER = [320, 240]  # 窗口中心点坐标
NUMSTARS = 150  # 星星数量


def init_star(steps=-1):
    """创建新的星星数据
    creates new star values

    :param steps: 初始步数，-1表示新星星，其他值表示已有星星的移动步数
    :return: 包含速度向量和位置坐标的列表 [velocity, position]
    """
    # 生成随机方向（0-99999之间的随机角度）
    dir = random.randrange(100000)

    # 计算速度乘数：如果steps=-1（新星星）则速度为1，否则基于步数计算
    steps_velocity = 1 if steps == -1 else steps * 0.09

    # 计算最终速度乘数：在0.4-1.0之间随机变化
    velmult = steps_velocity * (random.random() * 0.6 + 0.4)

    # 计算速度向量：使用正弦和余弦函数分解方向
    vel = [math.sin(dir) * velmult, math.cos(dir) * velmult]

    # 如果steps为None（特殊情况），返回基于步数的位置
    if steps is None:
        return [vel, [WINCENTER[0] + (vel[0] * steps), WINCENTER[1] + (vel[1] * steps)]]

    # 正常情况：返回速度向量和窗口中心位置
    return [vel, WINCENTER[:]]


def initialize_stars():
    """创建新的星空场
    creates a new starfield

    :return: 包含所有星星数据的列表
    """
    # 初始化随机数生成器
    random.seed()

    # 创建NUMSTARS个星星，每个星星有随机的初始步数（0到窗口中心X坐标之间）
    stars = [init_star(steps=random.randint(0, WINCENTER[0])) for _ in range(NUMSTARS)]

    # 移动星星一次，使它们分散开
    move_stars(stars)

    return stars


def draw_stars(surface, stars, color):
    """绘制（或清除）星星
    used to draw (and clear) the stars

    :param surface: 绘制表面
    :param stars: 星星数据列表
    :param color: 颜色值（RGB元组）
    """
    # 遍历所有星星，忽略速度向量，只使用位置
    for _, pos in stars:
        # 将位置坐标转换为整数
        pos = (int(pos[0]), int(pos[1]))
        # 在指定位置绘制一个像素点
        surface.set_at(pos, color)


def move_stars(stars):
    """动画化星星数据
    animate the star values

    :param stars: 星星数据列表
    """
    for vel, pos in stars:
        # 根据速度向量移动星星位置
        pos[0] = pos[0] + vel[0]
        pos[1] = pos[1] + vel[1]

        # 检查星星是否超出窗口边界
        if not 0 <= pos[0] <= WINSIZE[0] or not 0 <= pos[1] <= WINSIZE[1]:
            # 如果超出边界，重新初始化星星（从中心重新开始）
            vel[:], pos[:] = init_star()
        else:
            # 如果仍在窗口内，加速星星（每帧速度增加5%）
            vel[0] = vel[0] * 1.05
            vel[1] = vel[1] * 1.05


def main():
    """星空场主程序
    This is the starfield code
    """
    # 创建我们的星空场
    # create our starfield
    stars = initialize_stars()

    # 初始化并准备屏幕
    # initialize and prepare screen
    pg.init()
    screen = pg.display.set_mode(WINSIZE)
    pg.display.set_caption("pygame星空示例")
    pg.display.set_caption("pygame Stars Example")

    # 定义颜色
    white = 255, 240, 200  # 星星颜色（暖白色）
    black = 20, 20, 40  # 背景颜色（深蓝色）

    # 填充背景色
    screen.fill(black)

    # 创建时钟对象用于控制帧率
    clock = pg.time.Clock()

    # 主游戏循环
    # main game loop
    done = 0  # 循环控制标志
    while not done:
        # 使用黑色绘制星星（实际上是清除上一帧的星星）
        draw_stars(screen, stars, black)

        # 移动星星位置
        move_stars(stars)

        # 使用白色绘制星星（显示当前帧的星星）
        draw_stars(screen, stars, white)

        # 更新显示
        pg.display.update()

        # 处理事件
        for e in pg.event.get():
            # 退出事件：窗口关闭或按ESC键
            if e.type == pg.QUIT or (e.type == pg.KEYUP and e.key == pg.K_ESCAPE):
                done = 1
                break
            # 鼠标左键点击事件：移动星空场中心
            if e.type == pg.MOUSEBUTTONDOWN and e.button == 1:
                WINCENTER[:] = list(e.pos)  # 将中心点设置为鼠标点击位置

        # 控制帧率为50FPS
        clock.tick(50)

    # 退出pygame
    pg.quit()


# So `python -m pygame.example.stars` will work.
if __name__ == "__main__":
    main()

    # I prefer the time of insects to the time of stars.
    #
    #                              -- Wisława Szymborska
