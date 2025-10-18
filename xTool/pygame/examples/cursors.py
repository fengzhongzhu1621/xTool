"""pygame.examples.cursors
Click a button and the cursor will change.
This example will show you:
*The different types of cursors that exist
*How to create a cursor
*How to set a cursor
*How to make a simple button
"""

import os

import pygame as pg

from xTool.pygame import display
from xTool.pygame.draw.circle import check_circle

# 创建系统光标 - 使用Pygame内置的系统光标类型
system_cursor1 = pg.SYSTEM_CURSOR_CROSSHAIR  # 十字准星光标
system_cursor2 = pg.SYSTEM_CURSOR_HAND  # 手型光标
system_cursor3 = pg.SYSTEM_CURSOR_IBEAM  # 文本输入光标（I型光标）


# 创建颜色光标 - 使用Surface对象创建自定义颜色光标
surf = pg.Surface((40, 40))
surf.fill((120, 50, 50))  # 填充深红色
color_cursor = pg.cursors.Cursor((20, 20), surf)  # 创建光标，热点在中心


# 创建图像光标 - 从图像文件加载光标
main_dir = os.path.split(os.path.abspath(__file__))[0]  # 获取当前文件所在目录
image_name = os.path.join(main_dir, "data", "cursor.png")  # 图像文件路径
image = pg.image.load(image_name)  # 加载图像
image_cursor = pg.cursors.Cursor((image.get_width() // 2, image.get_height() // 2), image)  # 创建图像光标，热点在中心


# 创建位图光标 - 使用字符串数组定义光标形状
# 尺寸为24x24像素
thickarrow_strings = (
    "XX                      ",  # 箭头形状的字符串表示
    "XXX                     ",  # 'X'表示黑色像素
    "XXXX                    ",  # '.'表示白色像素
    "XX.XX                   ",  # ' '表示透明像素
    "XX..XX                  ",
    "XX...XX                 ",
    "XX....XX                ",
    "XX.....XX               ",
    "XX......XX              ",
    "XX.......XX             ",
    "XX........XX            ",
    "XX........XXX           ",
    "XX......XXXXX           ",
    "XX.XXX..XX              ",
    "XXXX XX..XX             ",
    "XX   XX..XX             ",
    "     XX..XX             ",
    "      XX..XX            ",
    "      XX..XX            ",
    "       XXXX             ",
    "       XX               ",
    "                        ",
    "                        ",
    "                        ",
)

# 编译字符串为位图光标
bitmap_cursor1 = pg.cursors.Cursor(
    (24, 24),  # 光标尺寸
    (0, 0),  # 热点位置（左上角）
    *pg.cursors.compile(thickarrow_strings, black="X", white=".", xor="o"),  # 编译字符串数组
)


# 创建预定义的位图光标 - 使用Pygame内置的位图光标
bitmap_cursor2 = pg.cursors.diamond  # 菱形光标


def main():
    """主函数 - 光标示例程序入口点"""
    pg.init()  # 初始化Pygame
    pg.font.init()  # 初始化字体模块
    font = pg.font.Font(None, 30)  # 创建30号字体
    font1 = pg.font.Font(None, 24)  # 创建24号字体

    # 创建显示窗口
    window = display.DisplayWindow(pg.Rect(0, 0, 500, 400), 0, 0)
    # 设置窗口标题
    window.set_caption("Cursors Example")
    bg = window.get_screen()
    # 填充浅蓝色背景
    _ = bg.fill((183, 201, 226))

    # 初始化圆圈 - 用于鼠标悬停效果演示
    radius1 = 40  # 圆圈1半径
    radius2 = 40  # 圆圈2半径
    radius3 = 40  # 圆圈3半径
    radius4 = 40  # 圆圈4半径
    radius5 = 40  # 圆圈5半径
    radius6 = 40  # 圆圈6半径
    radius7 = 40  # 圆圈7半径

    # 设置圆圈位置坐标
    pos_x1 = 82  # 圆圈1 x坐标
    pos_x2 = 138  # 圆圈2 x坐标
    pos_x3 = 194  # 圆圈3 x坐标
    pos_x4 = 250  # 圆圈4 x坐标
    pos_x5 = 306  # 圆圈5 x坐标
    pos_x6 = 362  # 圆圈6 x坐标
    pos_x7 = 418  # 圆圈7 x坐标

    pos_y1 = 140  # 圆圈1 y坐标
    pos_y2 = 220  # 圆圈2 y坐标
    pos_y3 = 140  # 圆圈3 y坐标
    pos_y4 = 220  # 圆圈4 y坐标
    pos_y5 = 140  # 圆圈5 y坐标
    pos_y6 = 220  # 圆圈6 y坐标
    pos_y7 = 140  # 圆圈7 y坐标

    # 绘制初始白色圆圈
    circle1 = pg.draw.circle(bg, (255, 255, 255), (pos_x1, pos_y1), radius1)
    circle2 = pg.draw.circle(bg, (255, 255, 255), (pos_x2, pos_y2), radius2)
    circle3 = pg.draw.circle(bg, (255, 255, 255), (pos_x3, pos_y3), radius3)
    circle4 = pg.draw.circle(bg, (255, 255, 255), (pos_x4, pos_y4), radius4)
    circle5 = pg.draw.circle(bg, (255, 255, 255), (pos_x5, pos_y5), radius5)
    circle6 = pg.draw.circle(bg, (255, 255, 255), (pos_x6, pos_y6), radius6)
    circle7 = pg.draw.circle(bg, (255, 255, 255), (pos_x7, pos_y7), radius7)

    # 初始化按钮 - 用于切换光标
    button_text = font1.render("Click here to change cursor", True, (0, 0, 0))  # 渲染按钮文本
    button = pg.draw.rect(
        bg,
        (180, 180, 180),
        (139, 300, button_text.get_width() + 5, button_text.get_height() + 50),
    )

    # 绘制按钮文本
    button_text_rect = button_text.get_rect(center=button.center)  # 文本居中
    _ = bg.blit(button_text, button_text_rect)

    # 更新显示
    pg.display.update()

    # 光标列表 - 包含所有可用的光标类型
    cursors = [
        system_cursor1,  # 系统十字光标
        color_cursor,  # 颜色光标
        system_cursor2,  # 系统手型光标
        image_cursor,  # 图像光标
        system_cursor3,  # 系统文本光标
        bitmap_cursor1,  # 位图箭头光标
        bitmap_cursor2,  # 位图菱形光标
    ]
    index = 0  # 当前光标索引
    pg.mouse.set_cursor(cursors[index])  # 设置初始光标

    pressed = False  # 鼠标按下状态标志
    clock = pg.time.Clock()  # 创建时钟对象用于控制帧率

    # 主游戏循环
    while True:
        clock.tick(50)  # 限制帧率为50FPS

        mouse_x, mouse_y = pg.mouse.get_pos()  # 获取鼠标当前位置

        # 检查鼠标是否在圆圈内并改变圆圈颜色（悬停效果）
        if check_circle(mouse_x, mouse_y, circle1.centerx, circle1.centery, radius1):
            circle1 = window.draw_circle((255, 0, 0), (pos_x1, pos_y1), radius1)  # 红色
        else:
            circle1 = window.draw_circle((255, 255, 255), (pos_x1, pos_y1), radius1)  # 白色

        if check_circle(mouse_x, mouse_y, circle2.centerx, circle2.centery, radius2):
            circle2 = window.draw_circle((255, 127, 0), (pos_x2, pos_y2), radius2)  # 橙色
        else:
            circle2 = window.draw_circle((255, 255, 255), (pos_x2, pos_y2), radius2)  # 白色

        if check_circle(mouse_x, mouse_y, circle3.centerx, circle3.centery, radius3):
            circle3 = window.draw_circle((255, 255, 0), (pos_x3, pos_y3), radius3)  # 黄色
        else:
            circle3 = window.draw_circle((255, 255, 255), (pos_x3, pos_y3), radius3)  # 白色

        if check_circle(mouse_x, mouse_y, circle4.centerx, circle4.centery, radius3):
            circle4 = window.draw_circle((0, 255, 0), (pos_x4, pos_y4), radius4)  # 绿色
        else:
            circle4 = window.draw_circle((255, 255, 255), (pos_x4, pos_y4), radius4)  # 白色

        if check_circle(mouse_x, mouse_y, circle5.centerx, circle5.centery, radius4):
            circle5 = window.draw_circle((0, 0, 255), (pos_x5, pos_y5), radius5)  # 蓝色
        else:
            circle5 = window.draw_circle((255, 255, 255), (pos_x5, pos_y5), radius5)  # 白色

        if check_circle(mouse_x, mouse_y, circle6.centerx, circle6.centery, radius6):
            circle6 = window.draw_circle((75, 0, 130), (pos_x6, pos_y6), radius6)  # 靛蓝色
        else:
            circle6 = window.draw_circle((255, 255, 255), (pos_x6, pos_y6), radius6)  # 白色

        if check_circle(mouse_x, mouse_y, circle7.centerx, circle7.centery, radius7):
            circle7 = window.draw_circle((148, 0, 211), (pos_x7, pos_y7), radius7)  # 紫色
        else:
            circle7 = window.draw_circle((255, 255, 255), (pos_x7, pos_y7), radius7)  # 白色

        # 更新光标类型显示文本
        _ = bg.fill((183, 201, 226), (0, 15, bg.get_width(), 50))  # 清除文本区域
        text1 = font.render((f"This is a {pg.mouse.get_cursor().type} cursor"), True, (0, 0, 0))
        text_rect1 = text1.get_rect(center=(bg.get_width() / 2, 40))  # 文本居中
        _ = bg.blit(text1, text_rect1)  # 绘制文本

        # 绘制按钮
        button = pg.draw.rect(
            bg,
            (100, 149, 240),  # 按钮颜色（蓝色）
            (139, 300, button_text.get_width() + 5, button_text.get_height() + 50),
        )
        bg.blit(button_text, button_text_rect)  # 绘制按钮文本

        # 检查按钮是否被点击并切换光标
        if button.collidepoint(mouse_x, mouse_y):  # 鼠标在按钮上
            button = pg.draw.rect(
                bg,
                (60, 100, 255),  # 悬停颜色（深蓝色）
                (
                    139,
                    300,
                    button_text.get_width() + 5,
                    button_text.get_height() + 50,
                ),
            )
            bg.blit(button_text, button_text_rect)

            # 检测鼠标点击（防止连续触发）
            if pg.mouse.get_pressed()[0] == 1 and pressed is False:  # 左键按下且之前未按下
                button = pg.draw.rect(
                    bg,
                    (0, 0, 139),  # 点击颜色（深蓝色）
                    (
                        139,
                        300,
                        button_text.get_width() + 5,
                        button_text.get_height() + 50,
                    ),
                )
                bg.blit(button_text, button_text_rect)
                index += 1  # 切换到下一个光标
                index %= len(cursors)  # 循环索引
                pg.mouse.set_cursor(cursors[index])  # 设置新光标
                pg.display.update()  # 更新显示
                pg.time.delay(40)  # 短暂延迟防止连续点击

        # 更新鼠标按下状态
        if pg.mouse.get_pressed()[0] == 1:
            pressed = True  # 鼠标按下
        elif pg.mouse.get_pressed()[0] == 0:
            pressed = False  # 鼠标释放

        # 处理事件
        for event in pg.event.get():
            if event.type == pg.QUIT:  # 窗口关闭事件
                pg.quit()  # 退出Pygame
                raise SystemExit  # 退出程序

        pg.display.update()  # 更新显示


if __name__ == "__main__":
    main()
