"""pygame.examples.scrap_clipboard

演示Pygame的剪贴板功能。
复制/粘贴！

键盘控制
-----------------

g - 获取并打印剪贴板中的数据类型。如果是图片，则显示在屏幕上。
p - 将文本放入剪贴板
a - 打印剪贴板中当前可用的数据类型
i - 将图片放入剪贴板
"""

import os
from io import BytesIO

import pygame as pg
import pygame.scrap as scrap


def usage():
    """打印使用说明"""
    print("按 'g' 键获取当前剪贴板中的所有数据")
    print("按 'p' 键将字符串放入剪贴板")
    print("按 'a' 键获取剪贴板中当前可用的数据类型列表")
    print("按 'i' 键将图片放入剪贴板")


# 获取当前文件所在目录
main_dir = os.path.split(os.path.abspath(__file__))[0]

# 初始化Pygame
pg.init()
# 创建200x200像素的窗口
screen = pg.display.set_mode((200, 200))
# 创建时钟对象用于控制帧率
c = pg.time.Clock()
# 主循环控制变量
going = True

# 初始化剪贴板模块并使用剪贴板模式
scrap.init()
scrap.set_mode(pg.SCRAP_CLIPBOARD)

# 显示使用说明
usage()

# 主事件循环
while going:
    # 处理所有事件
    for e in pg.event.get():
        # 退出事件：点击关闭按钮或按ESC键
        if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
            going = False

        # 按g键：获取剪贴板数据
        elif e.type == pg.KEYDOWN and e.key == pg.K_g:
            print("正在获取剪贴板中的不同数据..")
            # 遍历剪贴板中的所有数据类型
            for t in scrap.get_types():
                # 获取该类型的数据
                r = scrap.get(t)
                # 根据数据大小和内容进行不同处理
                if r and len(r) > 500:
                    print(f"类型 {t} : (大缓冲区，{len(r)} 字节)")
                elif r is None:
                    print(f"类型 {t} : None")
                else:
                    # 尝试将数据解码为ASCII文本显示
                    print(f"类型 {t} : '{r.decode('ascii', 'ignore')}'")
                # 如果是图片类型，尝试加载并显示
                if "image" in t:
                    namehint = t.split("/")[1]  # 从MIME类型中提取文件扩展名
                    if namehint in ["bmp", "png", "jpg"]:
                        # 使用BytesIO将字节数据转换为文件对象
                        f = BytesIO(r)
                        # 加载图片表面
                        loaded_surf = pg.image.load(f, "." + namehint)
                        # 将图片显示在屏幕上
                        screen.blit(loaded_surf, (0, 0))

        # 按p键：向剪贴板放置文本
        elif e.type == pg.KEYDOWN and e.key == pg.K_p:
            print("正在向剪贴板放置文本。")
            # 将文本数据放入剪贴板
            scrap.put(pg.SCRAP_TEXT, b"Hello. This is a message from scrap.")

        # 按a键：获取剪贴板中可用的数据类型
        elif e.type == pg.KEYDOWN and e.key == pg.K_a:
            print("正在获取剪贴板中的可用类型。")
            # 获取所有可用的数据类型
            types = scrap.get_types()
            print(types)
            # 检查特定类型是否存在
            if len(types) > 0:
                print(f"包含 {types[0]}: {scrap.contains(types[0])}")
                print("包含 _INVALID_: ", scrap.contains("_INVALID_"))

        # 按i键：向剪贴板放置图片
        elif e.type == pg.KEYDOWN and e.key == pg.K_i:
            print("正在向剪贴板放置图片。")
            scrap.set_mode(pg.SCRAP_CLIPBOARD)
            # 打开图片文件
            fp = open(os.path.join(main_dir, "data", "liquid.bmp"), "rb")
            # 读取图片数据
            buf = fp.read()
            # 将图片数据放入剪贴板
            scrap.put("image/bmp", buf)
            fp.close()

        # 按任意键或点击鼠标时重新显示使用说明
        elif e.type in (pg.KEYDOWN, pg.MOUSEBUTTONDOWN):
            usage()
    # 更新显示
    pg.display.flip()
    # 控制帧率为40FPS
    c.tick(40)

# 退出Pygame
pg.quit()
