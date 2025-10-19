#!/usr/bin/env python
"""pygame.examples.freetype_misc


Miscellaneous (or misc) means:
  "consisting of a mixture of various things that are not
   usually connected with each other"
   Adjective


All those words you read on computers, magazines, books, and such over the years?
Probably a lot of them were constructed with...

The FreeType Project:  a free, high-quality and portable Font engine.
https://freetype.org

Next time you're reading something. Think of them.


Herein lies a *BOLD* demo consisting of a mixture of various things.

        Not only is it a *BOLD* demo, it's an
        italics demo,
        a rotated demo,
        it's a blend,
        and is sized to go nicely with a cup of tea*.

        * also goes well with coffee.

Enjoy!
"""
import os

import pygame as pg
import pygame.freetype as freetype


def run():
    """主函数 - FreeType字体示例程序入口点"""
    pg.init()  # 初始化Pygame

    # 获取字体文件路径
    fontdir = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件所在目录
    font = freetype.Font(os.path.join(fontdir, "data", "sans.ttf"))  # 加载字体文件

    # 创建窗口和设置背景
    screen = pg.display.set_mode((800, 600))  # 创建800x600窗口
    screen.fill("gray")  # 填充灰色背景

    # 设置下划线调整和填充
    font.underline_adjustment = 0.5  # 下划线位置调整
    font.pad = True  # 启用填充
    # 渲染带下划线和斜体的"Hello World"（保持英文文本不变）
    font.render_to(
        screen,
        (32, 32),
        "Hello World",
        "red3",
        "dimgray",
        size=64,
        style=freetype.STYLE_UNDERLINE | freetype.STYLE_OBLIQUE,
    )
    font.pad = False  # 禁用填充

    # 渲染字母序列（保持英文文本不变）
    font.render_to(
        screen,
        (32, 128),
        "abcdefghijklm",
        "dimgray",
        "green3",
        size=64,
    )

    # 垂直文本演示（保持英文文本不变）
    font.vertical = True  # 启用垂直文本
    font.render_to(screen, (32, 200), "Vertical?", "blue3", None, size=32)
    font.vertical = False  # 禁用垂直文本

    # 旋转文本演示（保持英文文本不变）
    font.render_to(screen, (64, 190), "Let's spin!", "red3", None, size=48, rotation=55)
    font.render_to(screen, (160, 290), "All around!", "green3", None, size=48, rotation=-55)

    # 混合效果演示（保持英文文本不变）
    font.render_to(screen, (250, 220), "and BLEND", (255, 0, 0, 128), None, size=64)
    font.render_to(screen, (265, 237), "or BLAND!", (0, 0xCC, 28, 128), None, size=64)

    # 风车效果演示
    font.origin = True  # 启用原点模式
    for angle in range(0, 360, 45):  # 每45度绘制一个括号
        font.render_to(screen, (150, 420), ")", "black", size=48, rotation=angle)
    font.vertical = True  # 启用垂直文本
    for angle in range(15, 375, 30):  # 每30度绘制垂直文本
        font.render_to(screen, (600, 400), "|^*", "orange", size=48, rotation=angle)
    font.vertical = False  # 禁用垂直文本
    font.origin = False  # 禁用原点模式

    # Unicode字符演示（保持英文文本不变）
    utext = "I \u2665 Unicode"
    font.render_to(screen, (298, 320), utext, (0, 0xCC, 0xDD), None, size=64)

    # 心形符号演示
    utext = "\u2665"
    font.render_to(screen, (480, 32), utext, "gray", "red3", size=148)

    # SDL表面信息（保持英文文本不变）
    font.render_to(
        screen,
        (380, 380),
        "...yes, this is an SDL surface",
        "black",
        None,
        size=24,
        style=freetype.STYLE_STRONG,
    )

    # 垂直拉伸演示（保持英文文本不变）
    font.origin = True  # 启用原点模式
    r = font.render_to(
        screen,
        (100, 530),
        "stretch",
        "red3",
        None,
        size=(24, 24),
        style=freetype.STYLE_NORMAL,
    )
    font.render_to(
        screen,
        (100 + r.width, 530),
        " VERTICAL",
        "red3",
        None,
        size=(24, 48),
        style=freetype.STYLE_NORMAL,
    )

    # 水平拉伸演示（保持英文文本不变）
    r = font.render_to(
        screen,
        (100, 580),
        "stretch",
        "blue3",
        None,
        size=(24, 24),
        style=freetype.STYLE_NORMAL,
    )
    font.render_to(
        screen,
        (100 + r.width, 580),
        " HORIZONTAL",
        "blue3",
        None,
        size=(48, 24),
        style=freetype.STYLE_NORMAL,
    )

    pg.display.flip()  # 更新显示

    # 事件循环
    while True:
        if pg.event.wait().type in (pg.QUIT, pg.KEYDOWN, pg.MOUSEBUTTONDOWN):
            break  # 检测到退出事件时退出

    pg.quit()  # 退出Pygame


if __name__ == "__main__":
    run()
