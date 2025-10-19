"""pg.examples.go_over_there

这个简单的技术演示展示了Vector2.move_towards()的使用
使用多个圆圈来表示向量。一旦演示开始，每个圆圈将具有随机位置和速度。

鼠标控制：
* 使用鼠标点击设置新的目标位置

键盘控制：
* 按R键重新开始演示
"""

import random

import pygame as pg

version = pg.__version__  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]


# 常量定义
MIN_SPEED = 0.25  # 最小移动速度
MAX_SPEED = 5  # 最大移动速度
MAX_BALLS = 1600  # 最大球体数量
SCREEN_SIZE = pg.Vector2(1000, 600)  # 屏幕尺寸
CIRCLE_RADIUS = 5  # 圆圈半径

# 初始化Pygame
pg.init()
screen = pg.display.set_mode(SCREEN_SIZE)  # 创建屏幕
clock = pg.time.Clock()  # 创建时钟对象用于控制帧率

target_position = None  # 目标位置，初始为None
balls = []  # 存储所有球体的列表


class Ball:
    """球体类，表示一个移动的球体"""

    def __init__(self, position, speed):
        self.position = position  # 球体的当前位置
        self.speed = speed  # 球体的移动速度


def reset():
    """重置演示，重新生成所有球体"""
    global balls
    global target_position

    target_position = None  # 重置目标位置
    balls = []  # 清空球体列表

    # 生成指定数量的球体
    for _ in range(MAX_BALLS):
        # 随机生成球体位置
        pos = pg.Vector2(random.randint(0, int(SCREEN_SIZE.x)), random.randint(0, int(SCREEN_SIZE.y)))
        # 随机生成球体速度
        speed = random.uniform(MIN_SPEED, MAX_SPEED)

        # 创建球体对象并添加到列表
        b = Ball(pos, speed)
        balls.append(b)


# 初始化演示
reset()
delta_time = 0  # 时间增量，用于平滑移动
running = True  # 主循环控制标志

# 主游戏循环
while running:
    # 处理事件
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False  # 退出程序

        if event.type == pg.MOUSEBUTTONUP:
            # 鼠标点击时设置新的目标位置
            target_position = pg.mouse.get_pos()

        if event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                running = False  # ESC键退出

            if event.key == pg.K_r:
                reset()  # R键重置演示

    # 填充背景色（绿色）
    screen.fill((31, 143, 65))

    # 更新和绘制所有球体
    for o in balls:
        if target_position is not None:
            try:
                # 使用move_towards_ip方法让球体向目标位置移动
                # 移动距离 = 速度 × 时间增量
                o.position.move_towards_ip(target_position, o.speed * delta_time)
            except AttributeError:
                # 如果当前Pygame版本不支持move_towards_ip方法，抛出错误
                raise RuntimeError(
                    f"""Version {version} doesn't have Vector.move_towards_ip function.
                    Please update to >=2.1.3"""
                )

        # 绘制球体（浅绿色圆圈）
        pg.draw.circle(screen, (118, 207, 145), o.position, CIRCLE_RADIUS)

    # 更新显示
    pg.display.flip()

    # 控制帧率为60FPS，并获取时间增量
    delta_time = clock.tick(60)

    # 设置窗口标题显示帧率和球体数量
    pg.display.set_caption(f"fps: {round(clock.get_fps(), 2)}, ball count: {len(balls)}")

# 退出Pygame
pg.quit()
