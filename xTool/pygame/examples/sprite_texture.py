"""pygame.examples.sprite_texture

实验性示例！使用的API可能在下一个版本中消失（_sdl2是私有模块）。
Experimental! Uses APIs which may disappear in the next release (_sdl2 is private).

使用pygame.sprite的硬件加速Image对象。
Hardware accelerated Image objects with pygame.sprite.

_sdl2.video.Image是一种向后兼容的方式，用于在pygame.sprite组中使用Texture。
_sdl2.video.Image is a backwards compatible way with to use Texture with
pygame.sprite groups.
"""

import math
import os

import pygame as pg

# 检查SDL版本，需要pygame 2和SDL2
if pg.get_sdl_version()[0] < 2:
    raise SystemExit("此示例需要pygame 2和SDL2。")
    raise SystemExit("This example requires pygame 2 and SDL2.")

# 导入SDL2相关的硬件加速模块
from pygame._sdl2 import Image, Renderer, Texture, Window

# 设置数据目录路径
# 获取当前文件所在目录下的data文件夹
# 注意：此示例需要alien1.gif文件位于data目录中
data_dir = os.path.join(os.path.split(os.path.abspath(__file__))[0], "data")


def load_img(file):
    """加载图像文件

    :param file: 文件名
    :return: 加载的图像Surface对象
    """
    return pg.image.load(os.path.join(data_dir, file))


# 初始化显示模块
pg.display.init()
# 设置键盘重复：初始延迟10ms，重复间隔10ms
pg.key.set_repeat(10, 10)

# 创建可调整大小的窗口
win = Window("asdf", resizable=True)
# 创建渲染器
renderer = Renderer(win)
# 从图像Surface创建纹理
tex = Texture.from_surface(renderer, load_img("alien1.gif"))


class Something(pg.sprite.Sprite):
    """自定义精灵类，使用硬件加速的Image对象"""

    def __init__(self, img):
        """初始化精灵

        :param img: Image对象（硬件加速的图像）
        """
        pg.sprite.Sprite.__init__(self)

        # 设置精灵的矩形区域
        self.rect = img.get_rect()
        # 设置精灵的图像
        self.image = img

        # 将精灵尺寸放大5倍
        self.rect.w *= 5
        self.rect.h *= 5

        # 设置图像的旋转原点为中心点
        img.origin = self.rect.w / 2, self.rect.h / 2


# 创建第一个精灵：使用纹理的左半部分
# Image(tex, (0, 0, tex.width / 2, tex.height / 2)) 表示使用纹理的左半部分
sprite = Something(Image(tex, (0, 0, tex.width / 2, tex.height / 2)))
sprite.rect.x = 250  # 设置X坐标
sprite.rect.y = 50  # 设置Y坐标

# 创建第二个精灵：使用整个纹理
# sprite2 = Something(Image(sprite.image))  # 另一种创建方式（被注释）
sprite2 = Something(Image(tex))  # 使用整个纹理
sprite2.rect.x = 250
sprite2.rect.y = 250
# 将第二个精灵的尺寸缩小一半
sprite2.rect.w /= 2
sprite2.rect.h /= 2

# 创建精灵组并添加精灵
group = pg.sprite.Group()
group.add(sprite2)
group.add(sprite)

# 初始化变量
t = 0  # 时间计数器
running = True  # 主循环控制标志
clock = pg.time.Clock()  # 创建时钟对象用于控制帧率

# 设置渲染器的绘制颜色（红色）
renderer.draw_color = (255, 0, 0, 255)

# 主游戏循环
while running:
    # 处理事件
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
            elif event.key == pg.K_LEFT:
                sprite.rect.x -= 5  # 左移
            elif event.key == pg.K_RIGHT:
                sprite.rect.x += 5  # 右移
            elif event.key == pg.K_DOWN:
                sprite.rect.y += 5  # 下移
            elif event.key == pg.K_UP:
                sprite.rect.y -= 5  # 上移

    # 清空渲染器（准备新帧）
    renderer.clear()
    t += 1  # 增加时间计数器

    # 获取第一个精灵的图像对象
    img = sprite.image

    # 每帧增加旋转角度（1度）
    img.angle += 1

    # 尝试设置水平翻转和垂直翻转
    try:
        # 每50帧切换一次水平翻转（前25帧翻转，后25帧不翻转）
        img.flip_x = t % 50 < 25
        # 每100帧切换一次垂直翻转（前50帧翻转，后50帧不翻转）
        img.flip_y = t % 100 < 50
    except AttributeError:
        # 向后兼容性处理（针对pygame <= 2.1.2版本）
        # backwards compatibility for <=2.1.2
        img.flipX = t % 50 < 25  # pyright: ignore[reportAttributeAccessIssue]
        img.flipY = t % 100 < 50  # pyright: ignore[reportAttributeAccessIssue]

    # 动态改变图像颜色（红色通道）
    # 使用正弦函数创建平滑的颜色变化效果
    img.color[0] = int(255.0 * (0.5 + math.sin(0.5 * t + 10.0) / 2.0))  # pyright: ignore[reportIndexIssue]

    # 动态改变图像透明度
    # 使用正弦函数创建平滑的透明度变化效果
    img.alpha = int(255.0 * (0.5 + math.sin(0.1 * t) / 2.0))

    # 被注释的替代绘制方法
    # img.draw(dstrect=(x, y, 5 * img.srcrect['w'], 5 * img.srcrect['h']))

    # 绘制精灵组中的所有精灵
    group.draw(renderer)  # pyright: ignore[reportUnusedCallResult, reportArgumentType]

    # 呈现渲染结果（显示到屏幕）
    renderer.present()

    # 控制帧率为60FPS
    clock.tick(60)

    # 更新窗口标题显示当前帧率
    win.title = str(f"FPS: {clock.get_fps()}")

# 退出pygame
pg.quit()
