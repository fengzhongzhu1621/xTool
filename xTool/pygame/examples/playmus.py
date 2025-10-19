"""pygame.examples.playmus

一个简单的音乐播放器。

   使用pygame.mixer.music播放音频文件。

创建一个窗口来处理播放命令的键盘事件。


键盘控制
-----------------

空格键 - 播放/暂停切换
r键    - 倒带
f键    - 淡出
q键    - 停止

"""

import sys

import pygame as pg
import pygame.freetype


class Window:
    """应用程序的Pygame窗口

    Window实例管理窗口的创建和绘制。
    这是一个单例类，只能存在一个实例。

    """

    instance: None = None  # 单例实例

    def __new__(cls, *args, **kwds):
        """返回一个打开的Pygame窗口"""

        if Window.instance is not None:
            return Window.instance  # 如果实例已存在，直接返回  # pyright: ignore[reportUnreachable]

        self = object.__new__(cls)  # 创建新实例
        pg.display.init()  # 初始化显示模块

        # 创建600x400像素的窗口
        self.screen = pg.display.set_mode((600, 400))  # pyright: ignore[reportAttributeAccessIssue]
        # 保存单例实例
        Window.instance = self  # pyright: ignore[reportAttributeAccessIssue]

        return self

    def __init__(self, title):
        """初始化窗口"""
        pg.display.set_caption(title)  # 设置窗口标题
        self.text_color = (254, 231, 21, 255)  # 文本颜色（黄色）
        self.background_color = (16, 24, 32, 255)  # 背景颜色（深蓝色）
        # 填充背景色
        self.screen.fill(self.background_color)  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
        pg.display.flip()  # 更新显示

        pygame.freetype.init()  # 初始化freetype字体模块
        self.font = pygame.freetype.Font(None, 20)  # 创建默认字体，大小20
        self.font.origin = True  # 设置字体原点模式
        # 上行高度
        self.ascender = int(self.font.get_sized_ascender() * 1.5)  # pyright: ignore[reportCallIssue]
        # 下行高度
        self.descender = int(self.font.get_sized_descender() * 1.5)  # pyright: ignore[reportCallIssue]
        self.line_height = self.ascender - self.descender  # 行高

        # 在窗口中显示操作说明
        self.write_lines(
            "\n按'q'或'ESC'或关闭窗口退出\n"
            "按'空格键'播放/暂停\n"
            "按'r'键倒带到开头（重新开始）\n"
            "按'f'键在5秒内淡出音乐\n\n"
            "音乐结束时窗口会自动退出\n",
            0,  # 从第0行开始显示
        )

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()
        return False

    def close(self):
        """关闭窗口"""
        pg.display.quit()  # 退出显示模块
        Window.instance = None  # 清除单例实例

    def write_lines(self, text, line=0):
        """在窗口中写入多行文本

        参数:
        text - 要显示的文本（可以包含换行符）
        line - 起始行号（负数表示从底部开始）
        """
        w, h = self.screen.get_size()  # 获取窗口尺寸  # pyright: ignore[reportAttributeAccessIssue]
        line_height = self.line_height  # 行高
        nlines = h // line_height  # 计算窗口可容纳的行数
        if line < 0:
            line = nlines + line  # 负行号转换为从底部开始的行号
        # 逐行处理文本
        for i, text_line in enumerate(text.split("\n"), line):
            y = i * line_height + self.ascender  # 计算文本的y坐标
            # 首先清除该行
            self.screen.fill(  # pyright: ignore[reportAttributeAccessIssue]
                self.background_color, (0, i * line_height, w, line_height)
            )
            # 写入新文本
            self.font.render_to(
                self.screen, (15, y), text_line, self.text_color  # pyright: ignore[reportAttributeAccessIssue]
            )
        #
        pg.display.flip()  # 更新显示


def show_usage_message():
    """显示使用说明"""
    print("用法: python playmus.py <文件路径>")
    print("       或: python -m pygame.examples.playmus <文件路径>")


def main(file_path):
    """使用pg.mixer.music播放音频文件

    参数:
    file_path - 音频文件路径
    """

    with Window(file_path) as win:  # 使用上下文管理器创建窗口
        win.write_lines("加载中...", -1)  # 在窗口底部显示加载状态
        pg.mixer.init(frequency=44100)  # 初始化混音器，设置采样率为44100Hz
        try:
            paused = False  # 暂停状态标志
            pg.mixer.music.load(file_path)  # 加载音频文件

            # 确保事件循环至少每0.5秒运行一次
            pg.time.set_timer(pg.USEREVENT, 500)

            pg.mixer.music.play()  # 开始播放音乐
            win.write_lines("播放中...\n", -1)  # 更新状态显示

            # 主事件循环：当音乐正在播放或处于暂停状态时继续运行
            while pg.mixer.music.get_busy() or paused:
                e = pg.event.wait()  # 等待事件
                if e.type == pg.KEYDOWN:  # 处理键盘按下事件
                    key = e.key
                    if key == pg.K_SPACE:  # 空格键：播放/暂停切换
                        if paused:
                            pg.mixer.music.unpause()  # 恢复播放
                            paused = False
                            win.write_lines("播放中...\n", -1)
                        else:
                            pg.mixer.music.pause()  # 暂停播放
                            paused = True
                            win.write_lines("已暂停...\n", -1)
                    elif key == pg.K_r:  # r键：倒带或重新开始
                        if file_path[-3:].lower() in ("ogg", "mp3", "mod"):
                            status = "已倒带。"
                            pg.mixer.music.rewind()  # 倒带（仅支持特定格式）
                        else:
                            status = "已重新开始。"
                            pg.mixer.music.play()  # 重新开始播放
                        if paused:
                            pg.mixer.music.pause()  # 如果之前是暂停状态，保持暂停
                            win.write_lines(status, -1)
                    elif key == pg.K_f:  # f键：淡出效果
                        win.write_lines("淡出中...\n", -1)
                        pg.mixer.music.fadeout(5000)  # 在5秒内淡出音乐
                        # 淡出完成后get_busy()将返回False
                    elif key in [pg.K_q, pg.K_ESCAPE]:  # q键或ESC键：停止播放
                        paused = False
                        pg.mixer.music.stop()  # 立即停止播放
                        # get_busy()现在将返回False
                elif e.type == pg.QUIT:  # 窗口关闭事件
                    paused = False
                    pg.mixer.music.stop()  # 停止播放
                    # get_busy()现在将返回False
            pg.time.set_timer(pg.USEREVENT, 0)  # 停止定时器
        finally:
            pg.mixer.quit()  # 退出混音器
    pg.quit()  # 退出Pygame


if __name__ == "__main__":
    # 检查唯一的命令行参数（文件路径）
    if len(sys.argv) != 2:  # 如果没有提供文件路径参数
        show_usage_message()  # 显示使用说明
    else:
        main(sys.argv[1])  # 运行主函数，传入文件路径
