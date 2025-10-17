"""pygame.examples.blend_fill
Pygame 混合填充示例

演示如何使用Surface.fill()方法的不同混合模式来混合颜色。

键盘控制说明：

* 按 R, G, B 键分别增加红、绿、蓝颜色通道值
* 按 1-9 数字键设置颜色增加的步长范围
* 按以下键切换不同的混合模式：
  A - ADD（加法混合）, S - SUB（减法混合）, M - MULT（乘法混合）
  - - MIN（最小值混合）, + - MAX（最大值混合）

"""

import os

import pygame as pg
from pygame import K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9


def usage():
    """显示使用说明"""
    print("按 R, G, B 键分别增加红、绿、蓝颜色通道值")
    print("按 1-9 数字键设置颜色增加的步长范围")
    print("按以下键切换不同的混合模式：")
    print("A - ADD（加法混合）, S - SUB（减法混合）, M - MULT（乘法混合）")
    print("- - MIN（最小值混合）, + - MAX（最大值混合）")


main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")


def main():
    """主函数：演示颜色混合效果"""
    # 初始化变量
    color = [0, 0, 0]  # 当前颜色值 [R, G, B]
    changed = False  # 标记是否需要更新显示
    blendtype = 0  # 混合模式，默认为0（无混合）
    step = 5  # 颜色变化的步长

    # 初始化Pygame
    pg.init()

    # 创建640x480的窗口，32位颜色深度
    screen = pg.display.set_mode((640, 480), 0, 32)
    # 用灰色填充背景
    screen.fill((100, 100, 100))

    # 加载图像文件
    image = pg.image.load(os.path.join(data_dir, "liquid.bmp")).convert()
    # 创建用于混合的图像副本
    blendimage = pg.image.load(os.path.join(data_dir, "liquid.bmp")).convert()

    # 在屏幕上显示原始图像和混合图像
    screen.blit(image, (10, 10))  # 左侧：原始图像
    screen.blit(blendimage, (200, 10))  # 右侧：混合图像

    # 更新显示并设置键盘重复
    pg.display.flip()
    pg.key.set_repeat(500, 30)  # 设置按键重复：500ms延迟，30ms间隔
    usage()  # 显示使用说明

    going = True
    while going:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                going = False

            if event.type == pg.KEYDOWN:
                usage()  # 每次按键都显示使用说明

                if event.key == pg.K_ESCAPE:
                    going = False  # ESC键退出程序

                # 颜色通道控制
                if event.key == pg.K_r:
                    # 增加红色通道值
                    color[0] += step
                    if color[0] > 255:
                        color[0] = 0  # 超过255则归零
                    changed = True

                elif event.key == pg.K_g:
                    # 增加绿色通道值
                    color[1] += step
                    if color[1] > 255:
                        color[1] = 0
                    changed = True

                elif event.key == pg.K_b:
                    # 增加蓝色通道值
                    color[2] += step
                    if color[2] > 255:
                        color[2] = 0
                    changed = True

                # 混合模式切换
                elif event.key == pg.K_a:
                    blendtype = pg.BLEND_ADD  # 加法混合
                    changed = True
                elif event.key == pg.K_s:
                    blendtype = pg.BLEND_SUB  # 减法混合
                    changed = True
                elif event.key == pg.K_m:
                    blendtype = pg.BLEND_MULT  # 乘法混合
                    changed = True
                elif event.key == pg.K_PLUS:
                    blendtype = pg.BLEND_MAX  # 最大值混合
                    changed = True
                elif event.key == pg.K_MINUS:
                    blendtype = pg.BLEND_MIN  # 最小值混合
                    changed = True

                # 步长设置（1-9数字键）
                elif event.key in (K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9):
                    step = int(event.unicode)  # 将按键字符转换为数字

            # 如果颜色或混合模式发生变化，更新显示
            if changed:
                # 清空屏幕并重新绘制
                screen.fill((100, 100, 100))  # 灰色背景
                # 在屏幕坐标(10,10)位置绘制原始图像
                screen.blit(image, (10, 10))  # 左侧原始图像

                # 将原始图像复制到混合图像上
                blendimage.blit(image, (0, 0))
                # 应用颜色混合效果（对整个图像应用混合）
                blendimage.fill(color, None, blendtype)
                # 显示混合后的图像
                screen.blit(blendimage, (200, 10))

                # 打印当前颜色和像素信息
                print(f"当前颜色: {tuple(color)}, 像素(0,0)值: {[blendimage.get_at((0, 0))]}")
                changed = False  # 重置变化标记

                pg.display.flip()  # 更新显示

    pg.quit()


if __name__ == "__main__":
    main()
