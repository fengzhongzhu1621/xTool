import sys

import pygame

# pygame初始化
pygame.init()  # pyright: ignore[reportUnusedCallResult]

# 设置窗口大小为320x240像素
size = width, height = 320, 240
# 设置球的移动速度 [x方向速度, y方向速度]
speed = [2, 2]
# 定义黑色背景色
black = 0, 0, 0

# 创建游戏窗口
screen = pygame.display.set_mode(size)

# 加载球体图片并获取其矩形区域
ball = pygame.image.load("xTool/pygame/resources/intro_ball.gif")
# 此时 ball 在屏幕左上角
ballrect = ball.get_rect()

# 游戏主循环
while True:
    # 处理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()  # 退出程序

    # 移动球体
    ballrect = ballrect.move(speed)

    # 检测碰撞边界，实现反弹效果
    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]  # x方向速度反向
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]  # y方向速度反向

    # 用黑色填充屏幕，擦除屏幕上的内容
    screen.fill(black)  # pyright: ignore[reportUnusedCallResult]

    # 将球体绘制到屏幕上
    screen.blit(ball, ballrect)  # pyright: ignore[reportUnusedCallResult]

    # 刷新显示
    pygame.display.flip()
