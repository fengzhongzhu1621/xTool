"""pygame.examples.font_viewer
Scroll through your system fonts from a list of surfaces or one huge buffer.

This example exhibits:
* iterate over available fonts using font.get_fonts and font.SysFont()
* click and drag using mouse input
* scrolling with the scroll wheel
* save a surface to disk
* work with a very large surface
* simple mouse and keyboard scroll speed acceleration

By default this example uses the fonts returned by pygame.font.get_fonts()
and opens them using pygame.font.SysFont().
Alternatively, you may pass a path to the command line. The TTF files found
in that directory will be used instead.

Mouse Controls:
* Use the mouse wheel or click and drag to scroll

Keyboard Controls:
* Press up or down to scroll
* Press escape to exit
"""

import os
import sys

import pygame as pg
from pygame.surface import Surface

from xTool.pygame.font import get_font_list

use_big_surface = False  # 是否使用大表面模式：绘制到大缓冲区并保存PNG文件

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")


class FontViewer:
    """
    字体查看器类

    这个示例封装在FontViewer类中
    它初始化Pygame窗口，处理输入，并将自身绘制到屏幕上。
    """

    KEY_SCROLL_SPEED = 10  # 键盘滚动速度
    MOUSE_SCROLL_SPEED = 50  # 鼠标滚动速度

    def __init__(self):
        """初始化字体查看器"""
        pg.init()  # 初始化Pygame

        # 创建一个使用屏幕80%大小的窗口
        info = pg.display.Info()  # 获取显示信息
        w = info.current_w  # 屏幕宽度
        h = info.current_h  # 屏幕高度
        pg.display.set_mode((int(w * 0.8), int(h * 0.8)))  # 设置窗口大小
        self.font_size = h // 20  # 根据屏幕高度计算字体大小

        self.clock = pg.time.Clock()  # 创建时钟对象
        self.y_offset = 0  # Y轴偏移量（用于滚动）
        self.grabbed = False  # 鼠标抓取状态
        self.key_held = 0  # 按键持续时间（用于加速滚动）
        self.render_fonts("&N abcDEF789")  # 渲染字体预览

        # 根据参数选择显示模式
        if use_big_surface or "big" in sys.argv:
            self.render_surface()  # 大表面模式：生成完整表面
            self.display_surface()  # 显示大表面
            self.save_png()  # 保存为PNG文件
        else:
            self.display_fonts()  # 普通模式：逐个显示字体

    def get_font_list(self) -> list[str]:
        """
        获取字体列表

        使用font.get_fonts()生成系统字体列表，
        或从命令行路径获取字体文件。
        """
        return get_font_list(data_dir)

    def render_fonts(self, text="A display of font &N") -> None:
        """
        渲染字体预览

        构建一个包含表面和其累计高度的列表，
        用于字体列表中的每个字体。存储最大宽度和其他变量供后续使用。
        """
        font_size = self.font_size  # 字体大小
        color = (255, 255, 255)  # 字体颜色（白色）
        instruction_color = (255, 255, 0)  # 说明文字颜色（黄色）
        self.back_color = (0, 0, 0)  # 背景颜色（黑色）

        fonts = self.get_font_list()  # 获取字体列表和路径
        font_surfaces = []  # 字体表面列表
        total_height = 0  # 累计高度
        max_width = 0  # 最大宽度

        load_font = pg.font.Font if data_dir else pg.font.SysFont  # 根据路径选择字体加载方式

        # 在显示顶部显示使用说明
        font = pg.font.SysFont(pg.font.get_default_font(), font_size)  # 使用默认字体
        lines = (
            "Use the scroll wheel or click and drag",
            "to scroll up and down.",
            "Fonts that don't use the Latin Alphabet",
            "might render incorrectly.",
            f"Here are your {len(fonts)} fonts",
            "",
        )
        for line in lines:
            surf = font.render(line, 1, instruction_color, self.back_color)  # 渲染说明文字
            font_surfaces.append((surf, total_height))  # 添加到表面列表
            total_height += surf.get_height()  # 累计高度
            max_width = max(max_width, surf.get_width())  # 更新最大宽度

        # 渲染所有字体并存储累计高度
        for name in sorted(fonts):  # 按名称排序
            try:
                font = load_font(os.path.join(data_dir, name), font_size)  # 加载字体
            except OSError:  # 字体加载失败
                continue
            line = text.replace("&N", name)  # 替换占位符为字体名称
            try:
                surf = font.render(line, 1, color, self.back_color)  # 渲染字体预览
            except pg.error as e:  # 渲染错误
                print(e)
                break

            max_width = max(max_width, surf.get_width())  # 更新最大宽度
            font_surfaces.append((surf, total_height))  # 添加到表面列表
            total_height += surf.get_height()  # 累计高度

        # 存储变量供后续使用
        self.total_height = total_height  # 总高度
        self.max_width = max_width  # 最大宽度
        self.font_surfaces = font_surfaces  # 字体表面列表
        self.max_y = total_height - pg.display.get_surface().get_height()  # 最大Y偏移量

    def display_fonts(self):
        """
        Display the visible fonts based on the y_offset value(updated in
        handle_events) and the height of the pygame window.
        """
        pg.display.set_caption("Font Viewer")
        display = pg.display.get_surface()
        clock = pg.time.Clock()
        center = display.get_width() // 2

        while True:
            # draw visible surfaces
            display.fill(self.back_color)
            for surface, top in self.font_surfaces:
                bottom = top + surface.get_height()
                if bottom >= self.y_offset and top <= self.y_offset + display.get_height():
                    x = center - surface.get_width() // 2
                    display.blit(surface, (x, top - self.y_offset))
            # get input and update the screen
            if not self.handle_events():
                break
            pg.display.flip()
            clock.tick(30)

    def render_surface(self):
        """
        渲染大表面

        注意：此方法使用两倍内存，仅在big_surface设置为True或命令行中包含"big"时调用。

        可选地生成一个大缓冲区来绘制所有字体表面。
        这对于将显示保存为PNG文件是必要的，也可能对测试大表面有用。
        """

        large_surface = pg.surface.Surface((self.max_width, self.total_height)).convert()  # 创建大表面
        large_surface.fill(self.back_color)  # 填充背景色
        print("scrolling surface created")

        # 显示表面大小和内存使用情况
        byte_size = large_surface.get_bytesize()  # 获取每像素字节数
        total_size = byte_size * (self.max_width * self.total_height)  # 计算总内存使用量
        print(
            "Surface Size = {}x{} @ {}bpp: {:,.3f}mb".format(
                self.max_width, self.total_height, byte_size, total_size / 1000000.0
            )
        )

        y = 0  # 起始Y位置
        center = int(self.max_width / 2)  # 计算中心位置
        for surface, top in self.font_surfaces:
            w = surface.get_width()  # 获取表面宽度
            x = center - int(w / 2)  # 计算水平居中位置
            large_surface.blit(surface, (x, y))  # 将表面绘制到大表面上
            y += surface.get_height()  # 移动到下一行

        # 更新最大Y偏移量
        self.max_y = large_surface.get_height() - pg.display.get_surface().get_height()
        self.surface: Surface = large_surface  # 存储大表面  # pyright: ignore[reportUninitializedInstanceVariable]

    def display_surface(self, time=10):
        """
        Display the large surface created by the render_surface method. Scrolls
        based on the y_offset value(set in handle_events) and the height of the
        pygame window.
        """
        screen = pg.display.get_surface()

        # Create a Rect equal to size of screen. Then we can just change its
        # top attribute to draw the desired part of the rendered font surface
        # to the display surface
        rect = pg.rect.Rect(
            0,
            0,
            self.surface.get_width(),
            min(self.surface.get_height(), screen.get_height()),
        )

        x = int((screen.get_width() - self.surface.get_width()) / 2)
        going = True
        while going:
            if not self.handle_events():
                going = False
            screen.fill(self.back_color)
            rect.top = self.y_offset
            screen.blit(self.surface, (x, 0), rect)
            pg.display.flip()
            self.clock.tick(20)

    def save_png(self, name="font_viewer.png"):
        """保存PNG文件

        将大表面保存为PNG格式的图像文件。
        """
        pg.image.save(self.surface, name)  # 保存表面为PNG文件
        file_size = os.path.getsize(name) // 1024  # 计算文件大小（KB）
        print(f"font surface saved to {name}\nsize: {file_size:,}Kb")

    def handle_events(self):
        """
        处理事件

        此方法处理用户输入。当接收到pygame.QUIT事件或用户按下ESC键时返回False。
        y_offset根据鼠标和键盘输入进行更改。display_fonts()和display_surface()
        使用y_offset来滚动显示。
        """
        events = pg.event.get()  # 获取事件队列
        for e in events:
            if e.type == pg.QUIT:  # 窗口关闭事件
                return False
            elif e.type == pg.KEYDOWN:  # 按键事件
                if e.key == pg.K_ESCAPE:  # ESC键
                    return False
            elif e.type == pg.MOUSEWHEEL:  # 鼠标滚轮事件
                self.y_offset += e.y * self.MOUSE_SCROLL_SPEED * -1  # 根据滚轮方向调整偏移量
            elif e.type == pg.MOUSEBUTTONDOWN:  # 鼠标按下事件
                # 鼠标按下时进入拖拽模式
                self.grabbed = True
                pg.event.set_grab(True)  # 设置输入抓取
            elif e.type == pg.MOUSEBUTTONUP:  # 鼠标释放事件
                # 鼠标释放时退出拖拽模式
                self.grabbed = False
                pg.event.set_grab(False)  # 取消输入抓取

        # 允许使用键盘进行简单的加速滚动
        keys = pg.key.get_pressed()  # 获取按键状态
        if keys[pg.K_UP]:  # 上箭头键按下
            self.key_held += 1  # 增加按键持续时间
            self.y_offset -= int(self.KEY_SCROLL_SPEED * (self.key_held // 10))  # 加速向上滚动
        elif keys[pg.K_DOWN]:  # 下箭头键按下
            self.key_held += 1  # 增加按键持续时间
            self.y_offset += int(self.KEY_SCROLL_SPEED * (self.key_held // 10))  # 加速向下滚动
        else:
            self.key_held = 20  # 重置按键持续时间

        # 设置滚动偏移量并保持在0和max_y之间
        y = pg.mouse.get_rel()[1]  # 获取鼠标相对移动的Y分量
        if y and self.grabbed:  # 如果鼠标移动且处于抓取状态
            self.y_offset -= y  # 根据鼠标移动调整偏移量

        self.y_offset = min((max(self.y_offset, 0), self.max_y))  # 限制偏移量在有效范围内
        return True  # 继续运行


# 创建字体查看器实例并运行
viewer = FontViewer()
pg.quit()  # 退出Pygame
