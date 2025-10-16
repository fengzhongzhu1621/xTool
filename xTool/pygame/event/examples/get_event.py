# 示例文件展示基本的pygame游戏循环
import pygame

# pygame初始化设置
pygame.init()  # pyright: ignore[reportUnusedCallResult]

# 创建游戏窗口，设置分辨率为1280x720
screen: pygame.Surface = pygame.display.set_mode((1280, 720))

# 创建游戏时钟对象，用于控制帧率
clock = pygame.time.Clock()
running = True  # 游戏运行状态标志

# 游戏主循环
while running:
    # 处理事件
    # pygame.QUIT事件表示用户点击了关闭窗口按钮
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # 退出游戏循环

    # 用颜色填充屏幕，清除上一帧的内容
    _ = screen.fill("purple")

    # 在这里渲染你的游戏内容

    # 刷新显示，将你的工作呈现在屏幕上
    pygame.display.flip()

    # 限制帧率为60FPS
    clock.tick(60)  # pyright: ignore[reportUnusedCallResult]

# 退出pygame
pygame.quit()
