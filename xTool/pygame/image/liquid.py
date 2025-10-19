from math import sin

from pygame import Surface


def liquid(screen: Surface, bitmap: Surface, anim: float) -> None:
    # 定义网格划分：将屏幕划分为20x20像素的方块
    xblocks = range(0, 640, 20)  # x轴方向方块范围
    yblocks = range(0, 480, 20)  # y轴方向方块范围

    # 更新动画计数器
    anim = anim + 0.02

    # 遍历所有网格方块
    for x in xblocks:
        # 计算当前x位置对应的源图像x坐标（使用正弦波产生波动效果）
        xpos = (x + (sin(anim + x * 0.01) * 15)) + 20
        for y in yblocks:
            # 计算当前y位置对应的源图像y坐标（使用正弦波产生波动效果）
            ypos = (y + (sin(anim + y * 0.01) * 15)) + 20

            # 从源图像中提取20x20像素的方块并绘制到屏幕上
            # 参数说明：源图像，目标位置(x,y)，源图像区域(xpos,ypos,20,20)
            _ = screen.blit(bitmap, (x, y), (xpos, ypos, 20, 20))
