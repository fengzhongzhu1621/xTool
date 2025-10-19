"""pygame.examples.setmodescale

在高分辨率显示器（4k, 1080p）上，小图形游戏（640x480）会显示得非常小，
以至于无法游玩。SCALED标志会自动为你放大窗口。
游戏认为它是一个640x480的窗口，但实际上它可以更大。
鼠标事件会自动缩放，所以你的游戏不需要处理缩放。

将SCALED传递给pygame.display.set_mode意味着分辨率取决于
桌面大小，图形会被自动缩放。
"""

import pygame as pg

# 初始化Pygame
pg.init()

# 游戏内部分辨率（逻辑分辨率）
RES = (160, 120)
# 帧率
FPS = 30
# 创建时钟对象用于控制帧率
clock = pg.time.Clock()

# 打印所有可用的桌面尺寸
print("桌面尺寸:", pg.display.get_desktop_sizes())
# 创建显示窗口，使用SCALED和RESIZABLE标志
# SCALED: 自动缩放窗口以适应高分辨率显示器
# RESIZABLE: 窗口可调整大小
screen = pg.display.set_mode(RES, pg.SCALED | pg.RESIZABLE)

# 主循环

done = False  # 循环控制标志

# 动画变量：用于移动的小白点
# i: 水平位置，j: 垂直位置
i = 0
j = 0

# 获取渲染器信息（内部API，用于调试）
r_name, r_flags = pg.display._get_renderer_info()  # pyright: ignore[reportAttributeAccessIssue]
print("渲染器:", r_name, "标志:", bin(r_flags))
# 检查渲染器支持的标志
for flag, name in [
    (1, "software"),  # 软件渲染
    (2, "accelerated"),  # 硬件加速
    (4, "VSync"),  # 垂直同步
    (8, "render to texture"),  # 渲染到纹理
]:
    if flag & r_flags:
        print(name)  # 打印支持的渲染特性

# 主游戏循环
while not done:
    # 处理事件
    for event in pg.event.get():
        # 按Q键退出
        if event.type == pg.KEYDOWN and event.key == pg.K_q:
            done = True
        # 点击关闭按钮退出
        if event.type == pg.QUIT:
            done = True
        # 按F键切换全屏模式
        if event.type == pg.KEYDOWN and event.key == pg.K_f:
            pg.display.toggle_fullscreen()
        # 窗口大小改变事件
        if event.type == pg.VIDEORESIZE:
            # 内部API：处理窗口大小改变事件
            pg.display._resize_event(event)  # pyright: ignore[reportAttributeAccessIssue]

    # 更新动画位置
    i += 1  # 水平位置每次增加1
    i = i % screen.get_width()  # 循环到屏幕宽度边界
    j += i % 2  # 垂直位置根据水平位置的奇偶性增加
    j = j % screen.get_height()  # 循环到屏幕高度边界

    # 绘制图形
    screen.fill((255, 0, 255))  # 填充洋红色背景

    # 绘制黑色大圆（位置固定）
    pg.draw.circle(screen, (0, 0, 0), (100, 100), 20)
    # 绘制蓝色小圆（左上角）
    pg.draw.circle(screen, (0, 0, 200), (0, 0), 10)
    # 绘制红色大圆（右下角）
    pg.draw.circle(screen, (200, 0, 0), (160, 120), 30)
    # 绘制黄色对角线
    pg.draw.line(screen, (250, 250, 0), (0, 120), (160, 0))
    # 绘制移动的白色小圆（动画效果）
    pg.draw.circle(screen, (255, 255, 255), (i, j), 5)

    # 更新显示
    pg.display.flip()
    # 控制帧率
    clock.tick(FPS)

# 退出Pygame
pg.quit()
