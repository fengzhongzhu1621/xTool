"""pygame.examples.dropfile

Drag and drop an image on here.

Uses these events:

* DROPBEGIN
* DROPCOMPLETE
* DROPTEXT
* DROPFILE
"""

import pygame as pg

from xTool.pygame import display


def main():
    """主函数 - 拖放事件示例程序入口点"""
    pg.init()  # 初始化Pygame

    going = True  # 程序运行标志

    # 创建640x480像素的窗口
    window = display.DisplayWindow(pg.Rect(0, 0, 640, 480), 0, 0)
    surf = window.get_screen()
    font = pg.font.SysFont("Arial", 24)  # 创建Arial字体，24号大小
    clock = pg.time.Clock()  # 创建时钟对象用于控制帧率

    # 创建初始提示文本
    spr_file_text = font.render("Drag and drop a file or image!!", 1, (255, 255, 255))  # 白色文本
    spr_file_text_rect = spr_file_text.get_rect()  # 获取文本矩形区域
    spr_file_text_rect.center = surf.get_rect().center  # 文本居中显示

    spr_file_image = None  # 图像表面变量初始化
    spr_file_image_rect = None  # 图像矩形区域初始化

    # 主事件循环
    while going:
        # 处理事件队列
        for ev in pg.event.get():
            if ev.type == pg.QUIT:  # 窗口关闭事件
                going = False  # 退出循环
            elif ev.type == pg.DROPBEGIN:  # 拖放开始事件
                print(ev)  # 打印事件对象
                print("文件拖放开始!")
            elif ev.type == pg.DROPCOMPLETE:  # 拖放完成事件
                print(ev)  # 打印事件对象
                print("文件拖放完成!")
            elif ev.type == pg.DROPTEXT:  # 拖放文本事件
                print(ev)  # 打印事件对象
                # 更新显示文本为拖放的文本内容
                spr_file_text = font.render(ev.text, 1, (255, 255, 255))
                spr_file_text_rect = spr_file_text.get_rect()
                spr_file_text_rect.center = surf.get_rect().center  # 文本居中
            elif ev.type == pg.DROPFILE:  # 拖放文件事件
                print(ev)  # 打印事件对象
                # 更新显示文本为文件路径
                spr_file_text = font.render(ev.file, 1, (255, 255, 255))
                spr_file_text_rect = spr_file_text.get_rect()
                spr_file_text_rect.center = surf.get_rect().center  # 文本居中

                # 尝试打开文件，如果是图像文件则加载显示
                filetype = ev.file[-3:]  # 获取文件扩展名（后3个字符）
                if filetype in ["png", "bmp", "jpg"]:  # 检查是否为支持的图像格式
                    spr_file_image = pg.image.load(ev.file).convert()  # 加载并转换图像
                    spr_file_image.set_alpha(127)  # 设置半透明效果（alpha值127）
                    spr_file_image_rect = spr_file_image.get_rect()  # 获取图像矩形区域
                    spr_file_image_rect.center = surf.get_rect().center  # 图像居中显示

        # 绘制界面
        surf.fill((0, 0, 0))  # 填充黑色背景
        surf.blit(spr_file_text, spr_file_text_rect)  # 绘制文本
        if spr_file_image and spr_file_image_rect is not None:  # 如果有图像则绘制
            surf.blit(spr_file_image, spr_file_image_rect)  # 绘制图像

        pg.display.flip()  # 更新整个显示
        clock.tick(30)  # 限制帧率为30FPS

    pg.quit()  # 退出Pygame


if __name__ == "__main__":
    main()
