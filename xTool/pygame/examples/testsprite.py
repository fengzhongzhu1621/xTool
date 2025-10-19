"""pg.examples.testsprite

Like the testsprite.c that comes with libsdl, this pygame version shows
lots of sprites moving around.

It is an abomination of ugly code, and mostly used for testing.


See pg.examples.aliens for some prettyier code.

Pygame精灵测试示例

类似于libsdl自带的testsprite.c，这个Pygame版本展示大量精灵在屏幕上移动。
这是一个用于测试的丑陋代码，主要用于性能测试和渲染优化验证。

查看pg.examples.aliens获取更美观的代码示例。
"""

import os
import sys
from random import randint
from time import time
from typing import List

import pygame as pg

# 获取主目录和数据目录路径
main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "data")


# 配置参数：是否使用矩形更新优化
# 如果屏幕大部分被精灵覆盖，矩形更新优化效果不明显
update_rects = True
if "-update_rects" in sys.argv:
    update_rects = True
if "-noupdate_rects" in sys.argv:
    update_rects = False

# 是否包含静态精灵
use_static = False
if "-static" in sys.argv:
    use_static = True

# 是否使用分层脏矩形渲染
use_layered_dirty = False
if "-layered_dirty" in sys.argv:
    update_rects = True
    use_layered_dirty = True

# 显示模式标志位
flags = 0
if "-flip" in sys.argv:
    flags ^= pg.DOUBLEBUF  # 双缓冲模式

if "-fullscreen" in sys.argv:
    flags ^= pg.FULLSCREEN  # 全屏模式

if "-sw" in sys.argv:
    flags ^= pg.SWSURFACE  # 软件渲染

# RLE（运行长度编码）优化
use_rle = True

if "-hw" in sys.argv:
    flags ^= pg.HWSURFACE  # 硬件加速渲染
    use_rle = False  # 硬件渲染时禁用RLE

if "-scaled" in sys.argv:
    flags ^= pg.SCALED  # 缩放显示

# 屏幕尺寸设置
screen_dims = [640, 480]

# 从命令行参数获取屏幕高度
if "-height" in sys.argv:
    i = sys.argv.index("-height")
    screen_dims[1] = int(sys.argv[i + 1])

# 从命令行参数获取屏幕宽度
if "-width" in sys.argv:
    i = sys.argv.index("-width")
    screen_dims[0] = int(sys.argv[i + 1])

# 是否使用Alpha混合
use_alpha = "-alpha" in sys.argv

print(screen_dims)  # 打印屏幕尺寸


# class Thingy(pg.sprite.Sprite):
#    images = None
#    def __init__(self):
#        pg.sprite.Sprite.__init__(self)
#        self.image = Thingy.images[0]
#        self.rect = self.image.get_rect()
#        self.rect.x = randint(0, screen_dims[0])
#        self.rect.y = randint(0, screen_dims[1])
#        #self.vel = [randint(-10, 10), randint(-10, 10)]
#        self.vel = [randint(-1, 1), randint(-1, 1)]
#
#    def move(self):
#        for i in [0, 1]:
#            nv = self.rect[i] + self.vel[i]
#            if nv >= screen_dims[i] or nv < 0:
#                self.vel[i] = -self.vel[i]
#                nv = self.rect[i] + self.vel[i]
#            self.rect[i] = nv


class Thingy(pg.sprite.DirtySprite):
    """移动精灵类 - 继承自DirtySprite用于脏矩形优化"""

    images: List[pg.Surface] = []  # 类属性：精灵图像列表

    def __init__(self):
        """初始化移动精灵

        设置精灵的初始位置、速度和脏矩形标记
        """
        pg.sprite.DirtySprite.__init__(self)  # 调用父类初始化
        self.image = Thingy.images[0]  # 设置精灵图像
        self.rect = self.image.get_rect()  # 获取图像矩形区域
        # 随机设置精灵初始位置
        self.rect.x = randint(0, screen_dims[0])
        self.rect.y = randint(0, screen_dims[1])
        # 设置随机速度向量（x, y方向）
        # self.vel = [randint(-10, 10), randint(-10, 10)]  # 快速移动版本
        self.vel = [randint(-1, 1), randint(-1, 1)]  # 慢速移动版本
        self.dirty = 2  # 脏矩形标记：2表示需要重绘

    def update(self, *args, **kwargs):
        """更新精灵位置

        处理边界碰撞检测和位置更新
        """
        for i in [0, 1]:  # 遍历x和y方向
            # 计算新位置
            nv = self.rect[i] + self.vel[i]
            # 边界碰撞检测
            if nv >= screen_dims[i] or nv < 0:
                self.vel[i] = -self.vel[i]  # 反转速度方向
                nv = self.rect[i] + self.vel[i]  # 重新计算位置
            self.rect[i] = nv  # 更新位置


class Static(pg.sprite.DirtySprite):
    """静态精灵类 - 不移动的精灵，用于性能对比测试"""

    images: List[pg.Surface] = []  # 类属性：静态精灵图像列表

    def __init__(self):
        """初始化静态精灵

        设置精灵的初始位置（限制在屏幕3/4区域内）
        """
        pg.sprite.DirtySprite.__init__(self)  # 调用父类初始化
        self.image = Static.images[0]  # 设置精灵图像
        self.rect = self.image.get_rect()  # 获取图像矩形区域
        # 随机设置精灵初始位置（限制在屏幕3/4区域内）
        self.rect.x = randint(0, 3 * screen_dims[0] // 4)
        self.rect.y = randint(0, 3 * screen_dims[1] // 4)


def main(
    update_rects=True,
    use_static=False,
    use_layered_dirty=False,
    screen_dims=(640, 480),
    use_alpha=False,
    flags=0,
):
    """Show lots of sprites moving around

    Optional keyword arguments:
    update_rects - use the RenderUpdate sprite group class (default True)
    use_static - include non-moving images (default False)
    use_layered_dirty - Use the FastRenderGroup sprite group (default False)
    screen_dims - Pygame window dimensions (default [640, 480])
    use_alpha - use alpha blending (default False)
    flags - additional display mode flags (default no additional flags)

    显示大量移动的精灵

    可选关键字参数：
    update_rects - 使用RenderUpdate精灵组类（默认True）
    use_static - 包含非移动图像（默认False）
    use_layered_dirty - 使用FastRenderGroup精灵组（默认False）
    screen_dims - Pygame窗口尺寸（默认[640, 480]）
    use_alpha - 使用Alpha混合（默认False）
    flags - 额外的显示模式标志（默认无额外标志）

    """

    if use_layered_dirty:
        update_rects = True  # 分层脏矩形渲染需要启用矩形更新

    pg.init()  # 初始化Pygame，需要初始化时间模块以使用get_ticks()
    pg.display.init()  # 初始化显示模块

    # 创建显示窗口
    screen = pg.display.set_mode(screen_dims, flags, vsync="-vsync" in sys.argv)

    # 初始化游戏手柄（主要用于GP2X设备，以便可以退出程序）
    pg.joystick.init()
    num_joysticks = pg.joystick.get_count()
    if num_joysticks > 0:
        stick = pg.joystick.Joystick(0)
        stick.init()  # 初始化第一个手柄，现在我们将接收手柄事件

    # 清屏并刷新显示
    screen.fill([0, 0, 0])
    pg.display.flip()

    # 加载精灵图像
    sprite_surface = pg.image.load(os.path.join(data_dir, "asprite.bmp"))  # 移动精灵图像
    sprite_surface2 = pg.image.load(os.path.join(data_dir, "static.png"))  # 静态精灵图像

    # 设置颜色键（透明色）
    if use_rle:
        # 使用RLE加速的颜色键设置
        sprite_surface.set_colorkey([0xFF, 0xFF, 0xFF], pg.SRCCOLORKEY | pg.RLEACCEL)
        sprite_surface2.set_colorkey([0xFF, 0xFF, 0xFF], pg.SRCCOLORKEY | pg.RLEACCEL)
    else:
        # 普通颜色键设置
        sprite_surface.set_colorkey([0xFF, 0xFF, 0xFF], pg.SRCCOLORKEY)
        sprite_surface2.set_colorkey([0xFF, 0xFF, 0xFF], pg.SRCCOLORKEY)

    # 图像格式转换
    if use_alpha:
        # 转换为支持Alpha混合的格式
        sprite_surface = sprite_surface.convert_alpha()
        sprite_surface2 = sprite_surface2.convert_alpha()
    else:
        # 转换为标准显示格式
        sprite_surface = sprite_surface.convert()
        sprite_surface2 = sprite_surface2.convert()

    # 设置精灵类的图像属性
    Thingy.images = [sprite_surface]  # 移动精灵使用第一个图像
    if use_static:
        Static.images = [sprite_surface2]  # 静态精灵使用第二个图像

    # 设置精灵数量
    if len(sys.argv) > 1:
        try:
            numsprites = int(sys.argv[-1])  # 从命令行参数获取精灵数量
        except Exception:
            numsprites = 100  # 默认100个精灵
    else:
        numsprites = 100  # 默认100个精灵

    # 创建精灵组
    sprites = None
    if use_layered_dirty:
        # 使用分层脏矩形精灵组（优化渲染性能）
        sprites = pg.sprite.LayeredDirty()
    else:
        if update_rects:
            # 使用矩形更新精灵组
            sprites = pg.sprite.RenderUpdates()
        else:
            # 使用普通精灵组
            sprites = pg.sprite.Group()

    # 创建精灵实例并添加到精灵组
    for i in range(0, numsprites):
        if use_static and i % 2 == 0:
            sprites.add(Static())  # 每隔一个精灵添加静态精灵
        sprites.add(Thingy())  # 添加移动精灵

    # 初始化帧率和计时器
    frames = 0  # 帧计数器
    start = time()  # 开始时间

    # 创建背景表面
    background = pg.Surface(screen.get_size())
    background = background.convert()
    background.fill([0, 0, 0])  # 黑色背景

    # 主游戏循环
    going = True
    while going:
        # 如果不使用矩形更新，需要手动清屏
        if not update_rects:
            screen.fill([0, 0, 0])

        # 更新精灵状态
        if update_rects:
            sprites.clear(screen, background)  # 清除精灵区域
        sprites.update()  # 更新所有精灵

        # 绘制精灵并获取需要更新的矩形区域
        rects = sprites.draw(screen)
        # 更新显示
        if update_rects:
            pg.display.update(rects)  # 只更新变化的矩形区域
        else:
            pg.display.flip()  # 全屏刷新

        # 事件处理
        for event in pg.event.get():
            # 退出条件：关闭窗口、按键、手柄按钮
            if event.type in [pg.QUIT, pg.KEYDOWN, pg.QUIT, pg.JOYBUTTONDOWN]:
                going = False

        frames += 1  # 增加帧计数

    # 计算并打印帧率
    end = time()
    print(f"FPS: {frames / (end - start):f}")
    pg.quit()  # 退出Pygame


if __name__ == "__main__":
    main(update_rects, use_static, use_layered_dirty, screen_dims, use_alpha, flags)
