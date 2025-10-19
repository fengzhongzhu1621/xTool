import pygame as pg

pg.init()  # 初始化Pygame

RES = (160, 120)  # 初始窗口分辨率（宽度160，高度120）
FPS = 30  # 帧率设置为30FPS
clock = pg.time.Clock()  # 创建时钟对象用于控制帧率

# 创建可调整大小的窗口
screen = pg.display.set_mode(RES, pg.RESIZABLE)
# 禁用自动调整大小功能（实验性功能）
pg.display._set_autoresize(False)  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]

# 主循环

done = False  # 程序退出标志

i = 0  # 动画变量，用于控制白色圆圈的x坐标
j = 0  # 动画变量，用于控制白色圆圈的y坐标

while not done:
    # 处理事件队列
    for event in pg.event.get():
        if event.type == pg.KEYDOWN and event.key == pg.K_q:  # 按q键退出
            done = True
        if event.type == pg.QUIT:  # 点击窗口关闭按钮退出
            done = True
        # 注释掉的代码：处理窗口大小调整事件（旧版本）
        # if event.type==pg.WINDOWRESIZED:
        #    screen=pg.display.get_surface()
        if event.type == pg.VIDEORESIZE:  # 处理视频大小调整事件
            screen = pg.display.get_surface()  # 获取调整后的显示表面

    # 更新动画变量
    i += 1  # x坐标递增
    i = i % screen.get_width()  # 限制x坐标在屏幕宽度范围内（循环）
    j += i % 2  # y坐标根据x坐标的奇偶性递增
    j = j % screen.get_height()  # 限制y坐标在屏幕高度范围内（循环）

    # 绘制图形
    screen.fill((255, 0, 255))  # 用洋红色填充背景
    pg.draw.circle(screen, (0, 0, 0), (100, 100), 20)  # 在(100,100)绘制黑色圆圈（半径20）
    pg.draw.circle(screen, (0, 0, 200), (0, 0), 10)  # 在左上角绘制蓝色圆圈（半径10）
    pg.draw.circle(screen, (200, 0, 0), (160, 120), 30)  # 在(160,120)绘制红色圆圈（半径30）
    pg.draw.line(screen, (250, 250, 0), (0, 120), (160, 0))  # 绘制黄色对角线
    pg.draw.circle(screen, (255, 255, 255), (i, j), 5)  # 绘制移动的白色圆圈（半径5）

    pg.display.flip()  # 更新屏幕显示
    clock.tick(FPS)  # 控制帧率

pg.quit()  # 退出Pygame
