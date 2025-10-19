"""pygame.examples.moveit

这是Pygame教程"如何让物体移动"的完整最终示例。
它创建10个对象并在屏幕上为它们制作动画。

还有一个独立的玩家角色，可以用方向键控制。

注意：错误检查有点简单，但代码易于阅读。:]
幸运的是，这是Python，我们不需要处理一堆错误代码。
"""

import os

import pygame as pg

main_dir = os.path.split(os.path.abspath(__file__))[0]

# 屏幕的高度和宽度
WIDTH = 640  # 屏幕宽度
HEIGHT = 480  # 屏幕高度
# 精灵的高度和宽度
SPRITE_WIDTH = 80  # 精灵宽度
SPRITE_HEIGHT = 60  # 精灵高度


# 游戏对象类
class GameObject:
    """游戏对象类：表示游戏中的可移动对象

    属性:
    speed - 移动速度
    image - 对象图像
    pos - 对象位置矩形
    """

    def __init__(self, image, height, speed):
        """初始化游戏对象

        参数:
        image - 对象图像
        height - 初始高度位置
        speed - 移动速度
        """
        self.speed = speed
        self.image = image
        self.pos = image.get_rect().move(0, height)  # 创建矩形并移动到指定高度

    def move(self, up=False, down=False, left=False, right=False):
        """移动对象

        参数:
        up - 向上移动
        down - 向下移动
        left - 向左移动
        right - 向右移动
        """
        if right:
            self.pos.right += self.speed  # 向右移动
        if left:
            self.pos.right -= self.speed  # 向左移动
        if down:
            self.pos.top += self.speed  # 向下移动
        if up:
            self.pos.top -= self.speed  # 向上移动

        # 控制对象不离开屏幕视口
        if self.pos.right > WIDTH:  # 如果超出右边界
            self.pos.left = 0  # 从左侧重新出现
        if self.pos.top > HEIGHT - SPRITE_HEIGHT:  # 如果超出下边界
            self.pos.top = 0  # 从顶部重新出现
        if self.pos.right < SPRITE_WIDTH:  # 如果超出左边界
            self.pos.right = WIDTH  # 从右侧重新出现
        if self.pos.top < 0:  # 如果超出上边界
            self.pos.top = HEIGHT - SPRITE_HEIGHT  # 从底部重新出现


def load_image(name):
    """快速加载图像函数

    参数:
    name - 图像文件名

    返回:
    加载并转换后的图像表面
    """
    path = os.path.join(main_dir, "data", name)  # 构建完整路径
    return pg.image.load(path).convert()  # 加载图像并转换为显示格式


def main():
    """主函数：游戏主循环

    初始化游戏，创建对象，处理输入，更新显示
    """
    pg.init()  # 初始化pygame
    clock = pg.time.Clock()  # 创建时钟对象用于控制帧率
    screen = pg.display.set_mode((WIDTH, HEIGHT))  # 创建显示窗口

    # 加载游戏资源
    player = load_image("player1.gif")  # 加载玩家图像
    entity = load_image("alien1.gif")  # 加载外星人图像
    background = load_image("liquid.bmp")  # 加载背景图像

    # 缩放背景图像以填充窗口并成功覆盖旧的精灵位置
    background = pg.transform.scale2x(background)  # 第一次放大2倍
    background = pg.transform.scale2x(background)  # 第二次放大2倍（总共4倍）

    screen.blit(background, (0, 0))  # 初始绘制背景

    # 创建游戏对象列表
    objects = []
    p = GameObject(player, 10, 3)  # 创建玩家对象，高度10，速度3

    # 创建10个外星人对象，每个有不同的高度和速度
    for x in range(10):
        o = GameObject(entity, x * 40, x)  # 高度递增，速度递增
        objects.append(o)

    pg.display.set_caption("Move It!")  # 设置窗口标题

    # 简单的事件处理器，启用玩家输入
    while True:
        # 获取当前按下的所有键，当方向键被按住时移动
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:  # 上方向键
            p.move(up=True)
        if keys[pg.K_DOWN]:  # 下方向键
            p.move(down=True)
        if keys[pg.K_LEFT]:  # 左方向键
            p.move(left=True)
        if keys[pg.K_RIGHT]:  # 右方向键
            p.move(right=True)

        # 绘制背景
        screen.blit(background, (0, 0))

        # 处理事件
        for e in pg.event.get():
            # 退出屏幕时退出程序
            if e.type == pg.QUIT:
                return

        # 更新外星人对象
        for o in objects:
            # 用背景覆盖旧的外星人位置（擦除）
            screen.blit(background, o.pos, o.pos)

        for o in objects:
            o.move(right=True)  # 所有外星人向右移动
            screen.blit(o.image, o.pos)  # 绘制外星人

        screen.blit(p.image, p.pos)  # 绘制玩家

        clock.tick(60)  # 控制帧率为60FPS
        pg.display.update()  # 更新显示
        pg.time.delay(100)  # 添加延迟以控制游戏速度


if __name__ == "__main__":
    main()
    pg.quit()
