"""抗锯齿图形绘制示例 - Proof of concept gfxdraw example"""

import pygame
import pygame.gfxdraw


def main():
    """主函数：演示抗锯齿圆形绘制"""
    # pygame初始化
    pygame.init()
    # 创建500x500像素的窗口
    screen = pygame.display.set_mode((500, 500))
    # 用红色填充屏幕背景
    screen.fill((255, 0, 0))

    # 创建了一个与屏幕大小相同的透明画布
    # 创建带透明通道的Surface，用于绘制抗锯齿图形
    s = pygame.Surface(screen.get_size(), pygame.SRCALPHA, 32)

    # 在Surface上绘制一条黑色直线
    pygame.draw.line(s, (0, 0, 0), (250, 250), (250 + 200, 250))

    # 设置线宽为1像素
    width = 2
    # 绘制抗锯齿圆形
    for a_radius in range(width):
        radius = 200  # 圆形半径
        # 使用gfxdraw绘制抗锯齿圆形（中心点250,250，黑色）
        pygame.gfxdraw.aacircle(s, 250, 250, radius - a_radius, (0, 0, 0))

    # 将绘制好的Surface复制到屏幕上
    screen.blit(s, (0, 0))

    # 在屏幕上绘制一个绿色实心圆形
    pygame.draw.circle(screen, "green", (50, 100), 10)
    # 在绿色圆形上绘制黑色边框（仅绘制边框，不填充）
    pygame.draw.circle(screen, "black", (50, 100), 10, 1)

    # 刷新显示
    pygame.display.flip()

    # 事件循环，等待用户操作
    try:
        while True:
            # 等待事件
            event = pygame.event.wait()
            if event.type == pygame.QUIT:  # 点击关闭按钮
                break
            if event.type == pygame.KEYDOWN:  # 按键事件
                if event.key == pygame.K_ESCAPE or event.unicode == "q":  # ESC或Q键退出
                    break
            pygame.display.flip()  # 刷新显示
    finally:
        pygame.quit()  # 退出pygame


if __name__ == "__main__":
    main()  # 运行主函数
