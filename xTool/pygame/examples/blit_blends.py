"""pygame.examples.blit_blends
Pygame 混合模式示例

演示如何使用不同的混合模式来混合颜色。

同时展示了一些surfarray的技巧，包括如何进行加法混合。

键盘控制说明
-----------------

* R, G, B - 分别增加红、绿、蓝颜色分量
* A - 加法混合模式 (BLEND_ADD)
* S - 减法混合模式 (BLEND_SUB)
* M - 乘法混合模式 (BLEND_MULT)
* = 键 - 最大值混合模式 (BLEND_MAX)
* - 键 - 最小值混合模式 (BLEND_MIN)
* 1, 2, 3, 4 - 使用不同的图像

"""

import os
import time

import numpy
import pygame
import pygame as pg

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")

try:
    import pygame.surfarray
except ImportError:
    print("no surfarray for you!  install numpy")


def main():
    """主函数：演示混合模式效果"""
    # 初始化Pygame
    pg.init()
    pg.mixer.quit()  # 移除Debian squeeze的ALSA下溢消息
    screen = pg.display.set_mode((640, 480))  # 创建640x480窗口

    # 创建基础表面im1（红色背景）
    im1 = pg.Surface(screen.get_size())
    # im1= im1.convert()  # 可选的颜色格式转换
    im1.fill((100, 0, 0))  # 填充红色(RGB:100,0,0)

    # 创建第二个表面im2（绿色背景）
    im2 = pg.Surface(screen.get_size())
    im2.fill((0, 50, 0))  # 填充绿色(RGB:0,50,0)
    # 创建带透明度的副本
    # im3= im2.convert(SRCALPHA)  # 可选：创建带alpha通道的副本
    im3 = im2
    im3.set_alpha(127)  # 设置透明度为127（半透明）

    # 图像字典：按键映射到不同的图像
    images = {}
    images[pg.K_1] = im2  # 键1：绿色表面
    images[pg.K_2] = pg.image.load(os.path.join(data_dir, "chimp.png"))  # 键2：黑猩猩图像
    images[pg.K_3] = pg.image.load(os.path.join(data_dir, "alien3.gif"))  # 键3：外星人图像
    images[pg.K_4] = pg.image.load(os.path.join(data_dir, "liquid.bmp"))  # 键4：液体图像

    # 当前要混合的图像
    img_to_blit = im2.convert()  # 转换为标准格式
    iaa = img_to_blit.convert_alpha()  # 转换为带alpha通道的格式

    # 混合模式字典：按键映射到混合模式常量
    blits = {}
    blits[pg.K_a] = pg.BLEND_ADD  # A键：加法混合
    blits[pg.K_s] = pg.BLEND_SUB  # S键：减法混合
    blits[pg.K_m] = pg.BLEND_MULT  # M键：乘法混合
    blits[pg.K_EQUALS] = pg.BLEND_MAX  # =键：最大值混合
    blits[pg.K_MINUS] = pg.BLEND_MIN  # -键：最小值混合

    # 混合模式名称字典：用于调试输出
    blitsn = {}
    blitsn[pg.K_a] = "BLEND_ADD"
    blitsn[pg.K_s] = "BLEND_SUB"
    blitsn[pg.K_m] = "BLEND_MULT"
    blitsn[pg.K_EQUALS] = "BLEND_MAX"
    blitsn[pg.K_MINUS] = "BLEND_MIN"

    # 初始显示
    screen.blit(im1, (0, 0))  # 在屏幕上绘制im1
    pg.display.flip()  # 更新显示
    clock = pg.time.Clock()  # 创建时钟对象用于控制帧率
    print("初始像素值:%s:" % [im1.get_at((0, 0))])  # 打印左上角像素值

    going = True  # 主循环控制标志
    while going:
        clock.tick(60)  # 限制帧率为60FPS

        for event in pg.event.get():
            if event.type == pg.QUIT:
                going = False  # 窗口关闭事件
            if event.type == pg.KEYDOWN:
                usage()  # 显示使用说明

            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                going = False  # ESC键退出程序

            # 图像切换：按1-4键切换要混合的图像
            elif event.type == pg.KEYDOWN and event.key in images.keys():
                img_to_blit = images[event.key]  # 更新要混合的图像
                iaa = img_to_blit.convert_alpha()  # 更新带alpha通道的版本

            # 混合模式应用：按A/S/M/=/键应用不同的混合模式
            elif event.type == pg.KEYDOWN and event.key in blits.keys():
                t1 = time.time()  # 开始计时
                # blits是一个字典，按键映射到混合标志，如BLEND_ADD
                im1.blit(img_to_blit, (0, 0), None, blits[event.key])  # 应用混合模式
                t2 = time.time()  # 结束计时
                print("当前像素值:%s:" % [im1.get_at((0, 0))])  # 打印像素值
                print(f"执行时间:{t2 - t1}:")  # 打印执行时间

            # 计时测试：按T键测试所有混合模式的性能
            elif event.type == pg.KEYDOWN and event.key in [pg.K_t]:
                for bkey in blits.keys():
                    t1 = time.time()  # 开始计时

                    # 执行300次混合操作进行性能测试
                    for x in range(300):
                        im1.blit(img_to_blit, (0, 0), None, blits[bkey])

                    t2 = time.time()  # 结束计时

                    # 显示当前测试的混合模式名称
                    onedoing = blitsn[bkey]
                    print(f"混合模式:{onedoing}: 执行时间:{t2 - t1}:")

            # Alpha混合：按O键使用alpha通道进行混合
            elif event.type == pg.KEYDOWN and event.key in [pg.K_o]:
                t1 = time.time()
                # 使用带alpha通道的图像进行混合
                im1.blit(iaa, (0, 0))  # 应用alpha混合
                t2 = time.time()
                print("当前像素值:%s:" % [im1.get_at((0, 0))])
                print(f"执行时间:{t2 - t1}:")

            # 空间键：使用surfarray进行加法混合（无限制）
            elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                # 这种加法混合不限制两个表面的值
                # im1.set_alpha(127)
                # im1.blit(im1, (0,0))
                # im1.set_alpha(255)
                t1 = time.time()

                # 使用surfarray进行像素级加法操作
                im1p = pygame.surfarray.pixels2d(im1)  # 获取im1的2D像素数组
                im2p = pygame.surfarray.pixels2d(im2)  # 获取im2的2D像素数组
                im1p += im2p  # 像素级加法（可能超出255）
                del im1p  # 释放数组引用
                del im2p
                t2 = time.time()
                print("当前像素值:%s:" % [im1.get_at((0, 0))])
                print(f"执行时间:{t2 - t1}:")

            # Z键：使用surfarray进行带限制的加法混合
            elif event.type == pg.KEYDOWN and event.key in [pg.K_z]:
                t1 = time.time()
                # 使用3D像素数组进行更精确的颜色通道操作
                im1p = pygame.surfarray.pixels3d(im1)  # 获取im1的3D像素数组（RGB）
                im2p = pygame.surfarray.pixels3d(im2)  # 获取im2的3D像素数组
                im1p16 = im1p.astype(numpy.uint16)  # 转换为16位避免溢出
                im2p16 = im1p.astype(numpy.uint16)  # 转换为16位
                im1p16 += im2p16  # 16位加法
                im1p16 = numpy.minimum(im1p16, 255)  # 限制最大值不超过255
                pygame.surfarray.blit_array(im1, im1p16)  # 将结果写回表面

                del im1p  # 释放数组引用
                del im2p
                t2 = time.time()
                print("当前像素值:%s:" % [im1.get_at((0, 0))])
                print(f"执行时间:{t2 - t1}:")

            # RGB颜色增加：按R/G/B键分别增加对应颜色分量
            elif event.type == pg.KEYDOWN and event.key in [pg.K_r, pg.K_g, pg.K_b]:
                # 为每个像素增加对应的颜色分量
                colmap = {}  # 颜色映射字典
                colmap[pg.K_r] = 0x10000  # 红色分量：0x10000（16位颜色值）
                colmap[pg.K_g] = 0x00100  # 绿色分量：0x00100
                colmap[pg.K_b] = 0x00001  # 蓝色分量：0x00001
                im1p = pygame.surfarray.pixels2d(im1)  # 获取2D像素数组
                im1p += colmap[event.key]  # 增加对应的颜色分量
                del im1p  # 释放数组引用
                print("当前像素值:%s:" % [im1.get_at((0, 0))])

            # P键：打印当前像素值
            elif event.type == pg.KEYDOWN and event.key == pg.K_p:
                print("当前像素值:%s:" % [im1.get_at((0, 0))])

            # F键：使用alpha混合进行加法混合
            elif event.type == pg.KEYDOWN and event.key == pg.K_f:
                # 使用alpha混合进行加法混合，不限制两个表面的值

                t1 = time.time()
                im1.set_alpha(127)  # 设置im1的透明度为127
                im1.blit(im2, (0, 0))  # 使用alpha混合绘制im2
                im1.set_alpha(255)  # 恢复im1的不透明度

                t2 = time.time()
                print("当前像素值:%s:" % [im1.get_at((0, 0))])
                print(f"执行时间:{t2 - t1}:")

        # 每帧更新显示
        screen.blit(im1, (0, 0))  # 将im1绘制到屏幕上
        pg.display.flip()  # 更新显示

    pg.quit()  # 退出Pygame


def usage():
    """显示使用说明"""
    print("按1-5键切换要混合的图像")
    print("A - 加法混合, S - 减法混合, M - 乘法混合, - - 最小值混合, + - 最大值混合")
    print("T - 特殊混合模式的计时测试")


if __name__ == "__main__":
    usage()
    main()
