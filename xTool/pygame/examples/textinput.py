"""pg.examples.textinput

A little "console" where you can write in text.

Shows how to use the TEXTEDITING and TEXTINPUT events.

Pygame文本输入示例

一个可以输入文本的小型"控制台"。
展示如何使用TEXTEDITING和TEXTINPUT事件处理文本输入。
"""

import os
import sys
from typing import List

import pygame
import pygame as pg
import pygame.freetype as freetype

# 这个环境变量很重要
# 如果不设置，输入法候选列表将不会显示
os.environ["SDL_IME_SHOW_UI"] = "1"


class TextInput:
    """
    A simple TextInput class that allows you to receive inputs in pygame.

    一个简单的文本输入类，允许在Pygame中接收输入。
    """

    # 为每种语言添加字体名称，
    # 否则某些文本可能无法正确显示。
    FONT_NAMES = ",".join(
        str(x)
        for x in [
            "notosanscjktcregular",  # 思源黑体中日韩文常规体
            "notosansmonocjktcregular",  # 思源黑体等宽中日韩文常规体
            "notosansregular,",  # 思源黑体常规体
            "microsoftjhengheimicrosoftjhengheiuilight",  # 微软正黑体
            "microsoftyaheimicrosoftyaheiuilight",  # 微软雅黑体
            "msgothicmsuigothicmspgothic",  # MS Gothic字体
            "msmincho",  # MS Mincho字体
            "Arial",  # Arial字体
        ]
    )

    def __init__(self, prompt: str, pos, screen_dimensions, print_event: bool, text_color="white") -> None:
        """初始化文本输入组件

        Args:
            prompt: 提示符文本
            pos: 输入框位置
            screen_dimensions: 屏幕尺寸
            print_event: 是否打印事件信息
            text_color: 文本颜色
        """
        self.prompt = prompt  # 提示符
        self.print_event = print_event  # 是否打印事件
        # 聊天列表和输入框的位置
        self.CHAT_LIST_POS = pg.Rect((pos[0], pos[1] + 50), (screen_dimensions[0], 400))  # 聊天列表位置
        self.CHAT_BOX_POS = pg.Rect(pos, (screen_dimensions[1], 40))  # 输入框位置
        self.CHAT_LIST_MAXSIZE = 20  # 聊天列表最大容量

        # IME（输入法编辑器）相关状态变量
        self._ime_editing = False  # 是否正在编辑（输入法状态）
        self._ime_text = ""  # 当前输入的文本
        self._ime_text_pos = 0  # 文本插入位置
        self._ime_editing_text = ""  # 正在编辑的文本（输入法候选）
        self._ime_editing_pos = 0  # 编辑文本的插入位置
        self.chat_list: List[str] = []  # 聊天记录列表

        # 字体设置
        # 字体名称可以是逗号分隔的列表，系统会按顺序查找可用字体
        self.font = freetype.SysFont(self.FONT_NAMES, 24)  # 主字体（24像素）
        self.font_small = freetype.SysFont(self.FONT_NAMES, 16)  # 小字体（16像素）
        self.text_color = text_color  # 文本颜色

        print("Using font: " + self.font.name)  # 打印使用的字体名称

    def update(self, events) -> None:
        """
        Updates the text input widget

        更新文本输入组件状态
        """
        for event in events:
            # 处理按键按下事件
            if event.type == pg.KEYDOWN:
                if self.print_event:
                    print(event)  # 打印事件信息（调试用）

                # 如果正在输入法编辑状态，处理特殊逻辑
                if self._ime_editing:
                    if len(self._ime_editing_text) == 0:
                        self._ime_editing = False  # 编辑文本为空时退出编辑状态
                    continue  # 在编辑状态下跳过其他按键处理

                # 处理退格键
                if event.key == pg.K_BACKSPACE:
                    if len(self._ime_text) > 0 and self._ime_text_pos > 0:
                        # 删除光标前的一个字符
                        self._ime_text = (
                            self._ime_text[0 : self._ime_text_pos - 1] + self._ime_text[self._ime_text_pos :]
                        )
                        self._ime_text_pos = max(0, self._ime_text_pos - 1)  # 光标左移

                # 处理删除键
                elif event.key == pg.K_DELETE:
                    # 删除光标后的一个字符
                    self._ime_text = self._ime_text[0 : self._ime_text_pos] + self._ime_text[self._ime_text_pos + 1 :]

                # 处理左箭头键
                elif event.key == pg.K_LEFT:
                    self._ime_text_pos = max(0, self._ime_text_pos - 1)  # 光标左移

                # 处理右箭头键
                elif event.key == pg.K_RIGHT:
                    self._ime_text_pos = min(len(self._ime_text), self._ime_text_pos + 1)  # 光标右移

                # 处理回车键
                elif event.key in [pg.K_RETURN, pg.K_KP_ENTER]:
                    # 如果没有文本内容，阻止提交
                    if len(self._ime_text) == 0:
                        continue

                    # 将当前文本添加到聊天列表
                    self.chat_list.append(self._ime_text)
                    # 如果聊天列表超过最大容量，移除最早的消息
                    if len(self.chat_list) > self.CHAT_LIST_MAXSIZE:
                        self.chat_list.pop(0)
                    # 清空当前输入文本和光标位置
                    self._ime_text = ""
                    self._ime_text_pos = 0

            # 处理文本编辑事件（输入法候选状态）
            elif event.type == pg.TEXTEDITING:
                if self.print_event:
                    print(event)
                self._ime_editing = True  # 进入编辑状态
                self._ime_editing_text = event.text  # 设置编辑文本
                self._ime_editing_pos = event.start  # 设置编辑位置

            # 处理文本输入事件（最终确认的文本）
            elif event.type == pg.TEXTINPUT:
                if self.print_event:
                    print(event)
                self._ime_editing = False  # 退出编辑状态
                self._ime_editing_text = ""  # 清空编辑文本
                # 在光标位置插入新文本
                self._ime_text = (
                    self._ime_text[0 : self._ime_text_pos] + event.text + self._ime_text[self._ime_text_pos :]
                )
                self._ime_text_pos += len(event.text)  # 更新光标位置

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draws the text input widget onto the provided surface

        将文本输入组件绘制到指定的表面上
        """

        # 聊天列表更新
        chat_height = self.CHAT_LIST_POS.height / self.CHAT_LIST_MAXSIZE  # 计算每条消息的高度
        for i, chat in enumerate(self.chat_list):
            # 逐条渲染聊天消息
            self.font_small.render_to(
                screen,
                (self.CHAT_LIST_POS.x, self.CHAT_LIST_POS.y + i * chat_height),
                chat,
                self.text_color,
            )

        # 输入框更新
        start_pos = self.CHAT_BOX_POS.copy()  # 复制输入框起始位置

        # 将文本分为三部分：提示符+光标前文本、编辑文本、光标后文本
        ime_text_l = self.prompt + self._ime_text[0 : self._ime_text_pos]  # 左侧文本（提示符+光标前）
        ime_text_m = (
            self._ime_editing_text[0 : self._ime_editing_pos] + "|" + self._ime_editing_text[self._ime_editing_pos :]
        )  # 中间文本（编辑文本，包含光标）
        ime_text_r = self._ime_text[self._ime_text_pos :]  # 右侧文本（光标后）

        # 渲染左侧文本
        rect_text_l = self.font.render_to(screen, start_pos, ime_text_l, self.text_color)
        start_pos.x += rect_text_l.width  # 更新渲染位置

        # 编辑文本应该带下划线（输入法候选状态）
        rect_text_m = self.font.render_to(
            screen,
            start_pos,
            ime_text_m,
            self.text_color,
            None,
            freetype.STYLE_UNDERLINE,  # 添加下划线样式
        )
        start_pos.x += rect_text_m.width  # 更新渲染位置

        # 渲染右侧文本
        self.font.render_to(screen, start_pos, ime_text_r, self.text_color)


class Game:
    """
    A class that handles the game's events, mainloop etc.

    处理游戏事件、主循环等的类
    """

    # 常量定义
    # 帧率，程序的运行速度
    FPS = 50
    # 窗口尺寸
    SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
    BG_COLOR = "black"  # 背景颜色

    def __init__(self, caption: str) -> None:
        """初始化游戏

        Args:
            caption: 窗口标题
        """
        # 初始化
        pg.init()  # 初始化Pygame
        self.screen = pg.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))  # 创建显示窗口
        pg.display.set_caption(caption)  # 设置窗口标题
        self.clock = pg.time.Clock()  # 创建时钟对象用于控制帧率

        # 文本输入组件
        # 设置为true或在命令行参数中添加'showevent'来查看IME和KEYDOWN事件
        self.print_event = "showevent" in sys.argv  # 是否打印事件信息
        self.text_input = TextInput(
            prompt="> ",  # 提示符
            pos=(0, 20),  # 位置
            screen_dimensions=(self.SCREEN_WIDTH, self.SCREEN_HEIGHT),  # 屏幕尺寸
            print_event=self.print_event,  # 是否打印事件
            text_color="green",  # 文本颜色
        )

    def main_loop(self) -> None:
        """游戏主循环"""
        pg.key.start_text_input()  # 启动文本输入模式
        input_rect = pg.Rect(80, 80, 320, 40)  # 设置文本输入区域
        pg.key.set_text_input_rect(input_rect)  # 设置文本输入矩形区域

        while True:
            events = pg.event.get()  # 获取所有事件
            for event in events:
                if event.type == pg.QUIT:  # 处理退出事件
                    pg.quit()
                    return

            self.text_input.update(events)  # 更新文本输入组件状态

            # 屏幕更新
            self.screen.fill(self.BG_COLOR)  # 填充背景色
            self.text_input.draw(self.screen)  # 绘制文本输入组件

            pg.display.update()  # 更新显示
            self.clock.tick(self.FPS)  # 控制帧率


# 主循环处理
def main():
    """主函数 - 启动文本输入示例"""
    game = Game("Text Input Example")  # 创建游戏实例
    game.main_loop()  # 启动主循环


if __name__ == "__main__":
    main()  # 程序入口点
