"""
pygame.examples.mask

一个pygame.mask碰撞检测产品。




Brought

       to
             you
                     by

    the

pixels
               0000000000000
      and
         111111


这是32位：
    11111111111111111111111111111111

计算机"字"中有32或64位。
遮罩模块不是每个像素使用一个字，
而是用一个字表示32或64个像素。
正如您可以想象的，这使得处理速度更快，并节省内存。

计算密集型任务如碰撞检测和计算机视觉
从中受益匪浅。


这个模块也可以作为独立程序运行，接受
一个或多个图像文件名作为命令行参数。
"""

import os
import random
import sys

import pygame as pg


class Sprite:
    """
    移动精灵类，演示pg.mask.Mask对象之间的像素级碰撞检测
    """

    def __init__(self, pos, vel, surface, mask=None):
        """
        精灵初始化

        位置参数：
            pos: 精灵的位置（包含2个整数的序列）
            vel: 精灵的移动速度（包含2个整数的序列）
            surface: 精灵的图像（pg.Surface对象）
            mask: pg.mask.Mask对象（可选）
        """
        self.surface = surface  # 精灵的图像表面
        self.width, self.height = self.surface.get_size()  # 获取精灵尺寸

        # 设置遮罩：如果提供了遮罩则使用，否则从表面生成
        if mask is not None:
            self.mask = mask
        else:
            self.mask = pg.mask.from_surface(self.surface)

        self.pos = pg.Vector2(pos)  # 位置向量
        self.vel = pg.Vector2(vel)  # 速度向量

    def collide(self, sprite):
        """
        检测精灵是否发生碰撞，并在碰撞时解决碰撞

        位置参数：
            sprite: 要检测碰撞的另一个精灵
        """
        # 计算两个精灵之间的偏移量
        offset = [int(x) for x in sprite.pos - self.pos]

        # 检测遮罩重叠区域面积
        overlap = self.mask.overlap_area(sprite.mask, offset)
        if overlap == 0:
            return  # 没有重叠，直接返回

        # 计算碰撞法向量（碰撞方向）通过计算在x轴和y轴方向上微小偏移时的重叠面积差
        # 通过在不同方向上检测重叠面积的变化来计算法向量
        n_collisions = pg.Vector2(
            # x轴方向：检测左右偏移的重叠面积差
            self.mask.overlap_area(sprite.mask, (offset[0] + 1, offset[1]))
            - self.mask.overlap_area(sprite.mask, (offset[0] - 1, offset[1])),
            # y轴方向：检测上下偏移的重叠面积差
            self.mask.overlap_area(sprite.mask, (offset[0], offset[1] + 1))
            - self.mask.overlap_area(sprite.mask, (offset[0], offset[1] - 1)),
        )

        # 法向量计算：差值越大，说明该方向上的碰撞越强烈
        # 物理意义：这实际上是在计算碰撞表面的梯度（gradient）
        # 如果法向量为零，说明一个精灵完全在另一个内部
        if n_collisions.x == 0 and n_collisions.y == 0:
            return

        # 计算相对速度
        delta_vel = sprite.vel - self.vel

        # 计算碰撞冲量（基于物理的碰撞响应）（基于动量守恒），将冲量应用到两个精灵的速度上，实现弹性碰撞效果
        j = delta_vel * n_collisions / (2 * n_collisions * n_collisions)

        if j > 0:
            # 可以放大到2*j来获得弹性碰撞效果
            j *= 1.9
            # 应用冲量到两个精灵的速度上
            self.vel += [n_collisions.x * j, n_collisions.y * j]
            sprite.vel += [-j * n_collisions.x, -j * n_collisions.y]

        # # 分离精灵（注释掉的代码，用于物理分离）
        # c1 = -overlap / (n_collisions * n_collisions)
        # c2 = -c1 / 2
        # self.pos += [c2 * n_collisions.x, c2 * n_collisions.y]
        # sprite.pos += [(c1 + c2) * n_collisions.x, (c1 + c2) * n_collisions.y]

    def update(self):
        """
        移动精灵
        """
        self.pos += self.vel


def main(*args):
    """
    使用碰撞检测显示多个图像相互弹跳

    位置参数：
      一个或多个图像文件名。

    这个pg.masks演示将显示多个移动精灵相互弹跳。
    可以提供多个精灵图像。
    """

    if len(args) == 0:
        raise ValueError("需要至少一个图像文件名：未提供")

    # 初始化Pygame
    pg.init()

    # 设置屏幕
    screen_size = (640, 480)
    screen = pg.display.set_mode(screen_size)
    clock = pg.time.Clock()

    # 加载图像和生成遮罩
    images = []
    masks = []
    for image_path in args:
        # 加载图像并转换为带透明通道的格式
        images.append(pg.image.load(image_path).convert_alpha())
        # 从图像表面生成遮罩
        masks.append(pg.mask.from_surface(images[-1]))

    # 创建精灵
    sprites = []
    for i in range(20):  # 创建20个精灵
        j = i % len(images)  # 循环使用提供的图像
        sprite = Sprite(
            pos=(
                random.uniform(0, screen_size[0]),  # 随机x位置
                random.uniform(0, screen_size[1]),  # 随机y位置
            ),
            vel=(
                random.uniform(-5, 5),  # 随机x速度
                random.uniform(-5, 10),  # 随机y速度
            ),
            surface=images[j],  # 使用对应的图像
            mask=masks[j],  # 使用对应的遮罩
        )
        sprites.append(sprite)

    # 主游戏循环
    while True:
        # 处理事件
        for event in pg.event.get():
            if event.type in (pg.QUIT, pg.KEYDOWN):
                return  # 退出或按键时结束程序

        # 填充背景色（浅黄色）
        screen.fill((240, 220, 100))

        # 处理所有精灵
        for sprite_index, sprite in enumerate(sprites):
            # 检测与后续精灵的碰撞（避免重复检测）
            for other_sprite in sprites[sprite_index + 1 :]:
                sprite.collide(other_sprite)

            # 更新精灵位置
            sprite.update()

            # 屏幕边界检测和环绕
            # 如果精灵在屏幕左侧外
            if sprite.pos.x < -sprite.width:
                sprite.pos.x = screen_size[0]  # 移动到右侧
            # 如果精灵在屏幕右侧外
            elif sprite.pos.x > screen_size[0]:
                sprite.pos.x = -sprite.width  # 移动到左侧
            # 如果精灵在屏幕顶部外
            if sprite.pos.y < -sprite.height:
                sprite.pos.y = screen_size[1]  # 移动到底部
            # 如果精灵在屏幕底部外
            elif sprite.pos.y > screen_size[1]:
                sprite.pos.y = -sprite.height  # 移动到顶部

            # 绘制精灵到屏幕
            screen.blit(sprite.surface, sprite.pos)

        # 控制帧率为30FPS
        clock.tick(30)
        # 更新显示
        pg.display.flip()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: mask.py <IMAGE> [<IMAGE> ...]")
        print("Let many copies of IMAGE(s) bounce against each other")
        print("Press any key to quit")
        main_dir = os.path.split(os.path.abspath(__file__))[0]
        main(os.path.join(main_dir, "data", "alien1.png"), os.path.join(main_dir, "data", "player1.gif"))

    else:
        main(*sys.argv[1:])

    pg.quit()
