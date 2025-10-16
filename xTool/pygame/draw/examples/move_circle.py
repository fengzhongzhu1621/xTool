# 示例文件展示屏幕上移动的圆形
import pygame

# pygame初始化设置
pygame.init()  # pyright: ignore[reportUnusedCallResult]
# 创建游戏窗口，设置分辨率为1280x720
screen = pygame.display.set_mode((1280, 720))
# 创建游戏时钟对象，用于控制帧率
clock = pygame.time.Clock()
running = True  # 游戏运行状态标志
dt = 0  # 时间增量，用于帧率无关的物理计算

# 初始化玩家位置为屏幕中心
player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

# 游戏主循环
while running:
    # 处理事件
    # pygame.QUIT事件表示用户点击了关闭窗口按钮
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # 退出游戏循环

    # 用紫色填充屏幕，清除上一帧的内容
    screen.fill("purple")  # pyright: ignore[reportUnusedCallResult]

    # 在屏幕上绘制红色圆形，半径为40像素
    pygame.draw.circle(screen, "red", player_pos, 40)  # pyright: ignore[reportUnusedCallResult]

    # 获取键盘按键状态
    keys = pygame.key.get_pressed()
    # 根据WASD键控制圆形移动（y 轴向下）
    if keys[pygame.K_w]:  # W键：向上移动
        player_pos.y -= 300 * dt
    if keys[pygame.K_s]:  # S键：向下移动
        player_pos.y += 300 * dt
    if keys[pygame.K_a]:  # A键：向左移动
        player_pos.x -= 300 * dt
    if keys[pygame.K_d]:  # D键：向右移动
        player_pos.x += 300 * dt

    # 刷新显示，将绘制的内容呈现在屏幕上
    pygame.display.flip()

    # 限制帧率为60FPS
    # dt是自上一帧以来的时间增量（秒），用于实现帧率无关的物理计算
    dt = clock.tick(60) / 1000

# 退出pygame
pygame.quit()
