"""pygame.examples.scroll

一个缩放图像查看器，演示Surface.scroll功能

这个示例展示了一个可滚动的图像，缩放因子为8倍。
它使用Surface.scroll函数在显示表面上移动图像。
裁剪矩形保护边距区域。如果作为函数调用，
示例接受可选的图像文件路径。如果作为程序运行，
它接受可选的命令行文件路径参数。如果没有提供文件，
则使用默认图像文件。

运行时点击黑色三角形向三角形指向的方向移动一个像素。
或者使用方向键。关闭窗口或按ESC退出。
"""

import os
import sys

import pygame as pg
from pygame.transform import scale

from xTool.pygame.draw import draw_arrow

# 获取当前文件所在目录
main_dir = os.path.dirname(os.path.abspath(__file__))

# 方向常量定义
DIR_UP = 1  # 向上
DIR_DOWN = 2  # 向下
DIR_LEFT = 3  # 向左
DIR_RIGHT = 4  # 向右

# 缩放因子：8倍放大
zoom_factor = 8


def add_arrow_button(screen, regions, posn, direction):
    """添加箭头按钮到屏幕和区域映射表面

    参数:
        screen: 显示表面
        regions: 区域映射表面（用于检测点击）
        posn: 按钮位置
        direction: 箭头方向
    """
    # 在屏幕上绘制黑色箭头
    draw_arrow(screen, "black", posn, direction)
    # 在区域映射表面绘制带方向编码的箭头（用于鼠标点击检测）
    draw_arrow(regions, (direction, 0, 0), posn, direction)


def scroll_view(screen, image: pg.Surface, direction: int, view_rect):
    """滚动视图

    参数:
        screen: 显示表面
        image: 源图像
        direction: 滚动方向
        view_rect: 当前视图矩形
    """
    src_rect = None  # 源图像区域
    dst_rect = None  # 目标显示区域
    zoom_view_rect = screen.get_clip()  # 获取裁剪区域
    image_w, image_h = image.get_size()  # 图像尺寸

    # 根据滚动方向处理
    if direction == DIR_UP:
        # 向上滚动：检查是否到达图像顶部
        if view_rect.top > 0:
            # 屏幕向上滚动zoom_factor像素
            screen.scroll(dy=zoom_factor)
            # 视图矩形向上移动1像素
            view_rect.move_ip(0, -1)
            # 设置源区域为视图顶部1像素高的条带
            src_rect = view_rect.copy()
            src_rect.h = 1
            # 设置目标区域为显示区域顶部zoom_factor像素高的区域
            dst_rect = zoom_view_rect.copy()
            dst_rect.h = zoom_factor

    elif direction == DIR_DOWN:
        # 向下滚动：检查是否到达图像底部
        if view_rect.bottom < image_h:
            # 屏幕向下滚动zoom_factor像素
            screen.scroll(dy=-zoom_factor)
            # 视图矩形向下移动1像素
            view_rect.move_ip(0, 1)
            # 设置源区域为视图底部1像素高的条带
            src_rect = view_rect.copy()
            src_rect.h = 1
            src_rect.bottom = view_rect.bottom
            # 设置目标区域为显示区域底部zoom_factor像素高的区域
            dst_rect = zoom_view_rect.copy()
            dst_rect.h = zoom_factor
            dst_rect.bottom = zoom_view_rect.bottom

    elif direction == DIR_LEFT:
        # 向左滚动：检查是否到达图像左边界
        if view_rect.left > 0:
            # 屏幕向左滚动zoom_factor像素
            screen.scroll(dx=zoom_factor)
            # 视图矩形向左移动1像素
            view_rect.move_ip(-1, 0)
            # 设置源区域为视图左侧1像素宽的条带
            src_rect = view_rect.copy()
            src_rect.w = 1
            # 设置目标区域为显示区域左侧zoom_factor像素宽的区域
            dst_rect = zoom_view_rect.copy()
            dst_rect.w = zoom_factor

    elif direction == DIR_RIGHT:
        # 向右滚动：检查是否到达图像右边界
        if view_rect.right < image_w:
            # 屏幕向右滚动zoom_factor像素
            screen.scroll(dx=-zoom_factor)
            # 视图矩形向右移动1像素
            view_rect.move_ip(1, 0)
            # 设置源区域为视图右侧1像素宽的条带
            src_rect = view_rect.copy()
            src_rect.w = 1
            src_rect.right = view_rect.right
            # 设置目标区域为显示区域右侧zoom_factor像素宽的区域
            dst_rect = zoom_view_rect.copy()
            dst_rect.w = zoom_factor
            dst_rect.right = zoom_view_rect.right

    # 如果有源区域和目标区域，执行缩放和显示更新
    if src_rect is not None and dst_rect is not None:
        # 将源图像区域缩放到目标区域大小并显示
        scale(image.subsurface(src_rect), dst_rect.size, screen.subsurface(dst_rect))
        # 更新显示区域
        pg.display.update(zoom_view_rect)


def main(image_file=None):
    """主函数

    参数:
        image_file: 图像文件路径，如果为None则使用默认图像
    """
    # 如果没有提供图像文件，使用默认图像
    if image_file is None:
        image_file = os.path.join(main_dir, "data", "arraydemo.bmp")

    # 界面参数设置
    margin = 80  # 边距
    view_size = (30, 20)  # 视图大小（原始图像像素）
    # 缩放后的视图大小
    zoom_view_size = (view_size[0] * zoom_factor, view_size[1] * zoom_factor)
    # 窗口大小 = 缩放视图大小 + 两边边距
    win_size = (zoom_view_size[0] + 2 * margin, zoom_view_size[1] + 2 * margin)
    background_color = pg.Color("beige")  # 背景颜色

    # 初始化Pygame
    pg.init()
    pg.display.set_caption("Scroll Example")

    # 设置按键重复，以便按住键时可以连续滚动
    old_k_delay, old_k_interval = pg.key.get_repeat()
    pg.key.set_repeat(500, 30)  # 初始延迟500ms，重复间隔30ms

    try:
        # 创建显示窗口
        screen = pg.display.set_mode(win_size)
        screen.fill(background_color)
        pg.display.flip()

        # 加载图像
        image = pg.image.load(image_file).convert()
        image_w, image_h = image.get_size()

        # 检查图像尺寸是否足够大
        if image_w < view_size[0] or image_h < view_size[1]:
            print("源图像对于此示例来说太小了。")
            print("需要 %i x %i 或更大的图像。" % zoom_view_size)
            return

        # 创建区域映射表面（用于检测鼠标点击）
        regions = pg.Surface(win_size, 0, 24)
        # 添加四个方向的箭头按钮
        add_arrow_button(screen, regions, (40, win_size[1] // 2), DIR_LEFT)  # 左箭头
        add_arrow_button(screen, regions, (win_size[0] - 40, win_size[1] // 2), DIR_RIGHT)  # 右箭头
        add_arrow_button(screen, regions, (win_size[0] // 2, 40), DIR_UP)  # 上箭头
        add_arrow_button(screen, regions, (win_size[0] // 2, win_size[1] - 40), DIR_DOWN)  # 下箭头
        pg.display.flip()

        # 设置屏幕裁剪区域（保护边距）
        screen.set_clip((margin, margin, zoom_view_size[0], zoom_view_size[1]))

        # 创建视图矩形（表示当前显示的图像区域）
        view_rect = pg.Rect(0, 0, view_size[0], view_size[1])

        # 初始显示：将视图区域缩放到显示区域
        scale(
            image.subsurface(view_rect),  # 源图像区域
            zoom_view_size,  # 目标大小
            screen.subsurface(screen.get_clip()),  # 目标表面
        )
        pg.display.flip()

        # 滚动方向（用于鼠标拖动）
        direction = None

        # 创建时钟对象
        clock = pg.time.Clock()
        clock.tick()  # 初始化时钟

        # 主循环控制变量
        going = True

        # 主事件循环
        while going:
            # 获取所有事件
            events = pg.event.get()

            # 在循环中，如果按键被按住，滚动视图
            keys = pg.key.get_pressed()
            if keys[pg.K_UP]:
                scroll_view(screen, image, DIR_UP, view_rect)
            if keys[pg.K_DOWN]:
                scroll_view(screen, image, DIR_DOWN, view_rect)
            if keys[pg.K_LEFT]:
                scroll_view(screen, image, DIR_LEFT, view_rect)
            if keys[pg.K_RIGHT]:
                scroll_view(screen, image, DIR_RIGHT, view_rect)

            # 处理事件
            for e in events:
                # 退出事件
                if e.type == pg.QUIT:
                    going = False

                # 处理箭头上的鼠标按钮按下事件
                elif e.type == pg.MOUSEBUTTONDOWN:
                    # 从区域映射表面获取点击位置的颜色值，第一个分量就是方向编码
                    direction = regions.get_at(e.pos)[0]

                # 鼠标按钮释放时停止滚动
                elif e.type == pg.MOUSEBUTTONUP:
                    direction = None

            # 如果有方向设置（鼠标拖动），执行滚动
            if direction:
                scroll_view(screen, image, direction, view_rect)
            # 控制帧率为30FPS
            clock.tick(30)

    finally:
        # 恢复原来的按键重复设置
        pg.key.set_repeat(old_k_delay, old_k_interval)
        # 退出Pygame
        pg.quit()


if __name__ == "__main__":
    # 从命令行参数获取图像文件路径（如果有）
    image_file = sys.argv[1] if len(sys.argv) > 1 else None
    main(image_file)
