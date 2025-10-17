"""pygame.examples.aliens - 外星人入侵游戏示例

展示一个需要防御外星人入侵的迷你游戏。

这个示例展示了pygame的哪些功能？

* pg.sprite，Sprite和Group的区别
* 脏矩形优化以提高处理速度
* 使用pg.mixer.music播放音乐，包括淡出效果
* 使用pg.Sound播放音效
* 事件处理，键盘处理，QUIT处理
* 使用pg.time.Clock限制主循环帧率
* 全屏切换功能

控制方式
--------

* 左右方向键移动
* 空格键射击
* f键切换全屏模式

"""

import os
import random
from typing import Any, override

# import basic pygame modules
import pygame
import pygame as pg
from pygame import Rect
from pygame.font import Font
from pygame.mixer import Sound
from pygame.sprite import Group, GroupSingle, RenderUpdates
from pygame.surface import Surface

from xTool.pygame import display, image, init, quit, sound, sprite

# 游戏常量
MAX_SHOTS = 2  # 屏幕上最多允许的玩家子弹数量
ALIEN_ODDS = 22  # 新外星人出现的概率（1/22）
BOMB_ODDS = 60  # 新炸弹掉落的概率（1/60）
ALIEN_RELOAD = 12  # 新外星人出现的帧间隔
SCREENRECT = pg.Rect(0, 0, 640, 480)  # 屏幕矩形区域

main_dir = os.path.split(os.path.abspath(__file__))[0]
resource_dir = os.path.join(main_dir, "data")


# 每种游戏对象都有 init 和 update 函数
# update 函数每帧调用一次，用于更新对象的位置和状态
# Player 对象使用 move 函数而不是 update，因为它需要处理键盘输入信息


class Shot(sprite.Sprite):
    """玩家发射的子弹"""

    speed: int = -11  # 子弹速度（向上）

    def __init__(self, pos: tuple[int, int], *groups):
        super().__init__(*groups)

        # 加载子弹图像
        self.images = self.load_images([os.path.join(resource_dir, "shot.gif")])
        self.image = self.images[0]
        # 设置子弹的初始位置
        self.rect: Rect = self.get_rect_midbottom(pos)

    @override
    def update(self, *args, **kwargs):
        """每帧更新子弹状态

        每个tick我们向上移动子弹
        """
        # 向上移动
        _ = self.move_up(self.speed)


class Player(sprite.Sprite):
    """代表玩家的月球车类型汽车"""

    speed: int = 10  # 移动速度
    bounce: int = 24  # 弹跳效果参数
    gun_offset: int = -11  # 枪口水平偏移量

    def __init__(self, *groups) -> None:
        super().__init__(*groups)

        self.images: list[Surface] = self.load_flipx_images(os.path.join(resource_dir, "player1.gif"))  # 玩家图像列表
        self.image: Surface = self.images[0]  # 设置初始图像

        # 将玩家放置在屏幕底部中央
        self.rect: Rect = self.get_rect_midbottom(SCREENRECT)

        self.reloading: int = 0  # 重装状态
        self.origtop: int = self.rect.top  # 原始顶部位置

    def move(self, direction: int) -> None:
        """移动玩

        @direction int 小于 0 向左移动，大于 0 向右移动
        """
        _ = self.move_horizontal(direction, self.origtop, SCREENRECT, self.speed, self.bounce)

    def gunpos(self) -> tuple[int, int]:
        """获取枪口位置"""
        # self.facing: 玩家面向方向（1=向右，-1=向左）
        # self.gun_offset: 枪口相对于玩家中心的水平偏移量
        # self.rect.centerx: 玩家矩形的水平中心坐标
        # self.rect.top: 玩家矩形的顶部坐标
        #
        # 玩家向右 (facing=1):
        # 枪口位置 = 1 * 15 + 400 = 415 (玩家中心400，枪口在右侧15像素)
        #
        # 玩家向左 (facing=-1):
        # 枪口位置 = -1 * 15 + 400 = 385 (玩家中心400，枪口在左侧15像素)
        pos = self.facing * self.gun_offset + self.rect.centerx
        # 返回的坐标：(水平位置, 垂直位置)
        # 子弹会从这个坐标点开始飞行
        # 确保子弹从玩家的枪口而不是身体中心发射
        return pos, self.rect.top

    def fire(self, firing_state: bool, shoot_sound: Sound | sound.NoneSound, shots, all) -> None:
        """发射子弹"""
        # 如果不在重装状态、正在射击且子弹数量未达上限
        if not self.reloading and firing_state and len(shots) < MAX_SHOTS:
            # 创建子弹
            _ = Shot(self.gunpos(), shots, all)
            # 播放射击音效
            _ = shoot_sound.play()

        # 更新重装状态
        self.reloading = firing_state


class Alien(sprite.Sprite):
    """外星人飞船，缓慢在屏幕上移动"""

    speed: int = 13  # 移动速度
    animcycle: int = 12  # 动画循环帧数

    def __init__(self, *groups) -> None:
        super().__init__(*groups)

        # 加载多个动画帧
        self.images = self.load_images(
            [
                os.path.join(resource_dir, "alien1.gif"),
                os.path.join(resource_dir, "alien2.gif"),
                os.path.join(resource_dir, "alien3.gif"),
            ]
        )
        # 选择第一帧
        self.image: Surface = self.images[0]  # 设置初始图像
        self.rect: Rect = self.image.get_rect()  # 获取矩形区域

        # 随机选择移动方向，并计算移动距离
        self.facing: int = random.choice((-1, 1)) * Alien.speed
        self.frame: int = 0  # 动画帧计数器

        # 如果向左移动，从屏幕右侧开始
        if self.facing < 0:
            self.rect.right = SCREENRECT.right

    @override
    def update(self, *args, **kwargs):
        """更新外星人状态"""
        # 水平移动外星人
        self.rect.move_ip(self.facing, 0)

        # 如果碰到屏幕边缘，改变方向并下移一行
        if not self.in_screen(SCREENRECT):
            self.facing = -self.facing  # 水平反向移动
            self.rect = self.move_next_line(SCREENRECT)

        # 更新动画帧
        self.frame = self.frame + 1

        # 循环播放3帧动画，每次更新时切换图片
        self.image = self.images[self.frame // self.animcycle % 3]


class Explosion(sprite.Sprite):
    """An explosion. Hopefully the Alien and not the player!"""

    defaultlife = 12  # 爆炸持续的游戏帧数
    animcycle = 3  # 动画切换速度（每3帧切换一次图像）
    images: list[pg.Surface] = []  # 存储爆炸动画帧的列表

    def __init__(self, actor: pygame.sprite.Sprite, *groups):
        super().__init__(*groups)

        # 存储爆炸动画帧的列表
        self.images = self.load_flipxy_iamges(os.path.join(resource_dir, "explosion1.gif"))
        self.image = self.images[0]

        # 将爆炸效果的矩形边界定位到被炸对象（actor）的中心点
        self.rect = self.get_rect_center(actor.rect)  # pyright: ignore[reportAttributeAccessIssue]
        self.life = self.defaultlife

    @override
    def update(self, *args, **kwargs):
        """Called every time around the game loop.

        Show the explosion surface for 'defaultlife'.
        Every game tick(update), we decrease the 'life'.

        Also we animate the explosion.
        """
        self.life: int = self.life - 1
        self.image = self.images[self.life // self.animcycle % 2]
        if self.life <= 0:
            # 爆炸消失
            self.kill()


class Bomb(sprite.Sprite):
    """外星人投掷的炸弹"""

    speed = 9  # 炸弹下落速度

    def __init__(self, alien, explosion_group, *groups):
        super().__init__(*groups)

        self.images = self.load_images([os.path.join(resource_dir, "bomb.gif")])
        self.image = self.images[0]  # 设置炸弹图像
        # 在外星人下方5像素位置创建炸弹
        self.rect = self.get_rect_midbottom(alien.rect.move(0, 5))

        self.explosion_group = explosion_group  # 爆炸效果组

    @override
    def update(self, *args, **kwargs):
        """每帧更新炸弹状态

        每帧我们将精灵'rect'向下移动
        当它到达底部时：

        - 创建爆炸效果
        - 移除炸弹
        """
        # 向下移动
        _ = self.move_down(self.speed)
        if self.rect.bottom >= 470:  # 如果炸弹到达屏幕底部
            # 创建爆炸效果，添加到爆炸组中，便于统一更新和渲染
            Explosion(self, self.explosion_group)
            # 移除炸弹对象，但爆炸继续播放
            self.kill()


class Score(pg.sprite.Sprite):
    """用于跟踪分数"""

    def __init__(self, *groups) -> None:
        super().__init__(*groups)  # 调用父类构造函数

        self.total: int = 0

        self.font: Font = pg.font.Font(None, 20)  # 创建字体
        self.font.set_italic(1)  # 设置斜体

        self.color: str = "white"  # 分数颜色
        self.lastscore: int = -1  # 上一次分数

        self.update()  # 初始更新
        self.rect: Rect = self.image.get_rect().move(10, 450)  # 设置显示位置

    def incr(self) -> None:
        self.total += 1

    def get_total(self) -> int:
        return self.total

    @override
    def update(self, *args, **kwargs) -> None:
        """只有当分数发生变化时才更新"""
        if self.total != self.lastscore:  # 如果分数有变化
            self.lastscore = self.total  # 更新上一次分数
            # 渲染分数图像
            msg = f"Score: {self.total}"  # 创建分数文本
            self.image: Surface = self.font.render(msg, 0, self.color)


def main(winstyle=0) -> None:
    """游戏主函数"""
    ###############################################################################################################
    # 初始化
    init.init_game()
    # 设置显示模式
    display_screen = display.DisplayWindow(SCREENRECT, winstyle, 32)
    screen = display_screen.set_model()

    ###############################################################################################################
    # 装饰游戏窗口
    # 设置窗口图标
    icon = image.load_image(os.path.join(resource_dir, "alien1.gif"))
    display_screen.set_icon(icon, (32, 32))
    # 设置窗口标题
    display_screen.set_caption("Pygame Aliens")
    # 隐藏鼠标光标
    display_screen.hide_mouse()
    # 创建背景，平铺背景图像
    background = display_screen.blit_background(os.path.join(resource_dir, "background.gif"))
    display_screen.flip()
    # 播放背景音乐
    display_screen.play_background_sound(os.path.join(resource_dir, "house_lo.wav"))

    ###############################################################################################################
    # 加载音效
    boom_sound = sound.load_sound(os.path.join(resource_dir, "boom.wav"))  # 爆炸音效
    shoot_sound = sound.load_sound(os.path.join(resource_dir, "car_door.wav"))  # 射击音效

    # 初始化游戏组
    aliens: Group[Alien] = pg.sprite.Group()  # 外星人组
    shots: Group[Any] = pg.sprite.Group()  # 子弹组
    bombs: Group[Bomb] = pg.sprite.Group()  # 炸弹组
    all: RenderUpdates[Any] = pg.sprite.RenderUpdates()  # 所有需要更新的精灵组
    lastalien: GroupSingle[Any] = pg.sprite.GroupSingle()  # 最后一个外星人（用于投掷炸弹）

    # 创建一些初始值
    alienreload = ALIEN_RELOAD  # 外星人重装计数器
    clock = pg.time.Clock()  # 游戏时钟

    # 初始化起始精灵
    # all = Player + aliens group + score
    # lastalien = aliens group 中最新的一个
    player = Player(all)  # 创建玩家
    Alien(aliens, all, lastalien)  # 创建初始外星人
    score: Score = Score(all)  # 创建分数显示
    if pg.font:
        all.add(score)  # 添加分数显示

    # 当玩家存活时运行主循环
    while player.alive():
        # 获取输入
        for event in pg.event.get():
            if event.type == pg.QUIT:  # 退出事件
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:  # ESC键退出
                return
            if event.type == pg.KEYDOWN:  # 按键事件
                if event.key == pg.K_f:
                    # f键切换全屏
                    screen: Surface = display_screen.switch_screen()

        keystate = pg.key.get_pressed()  # 获取按键状态

        # 清除/擦除上次绘制的精灵
        all.clear(screen, background)

        # 更新所有精灵
        all.update()

        # 移动玩家
        direction = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]  # 计算移动方向
        player.move(direction)  # 移动玩家
        firing = keystate[pg.K_SPACE]  # 射击状态

        # 发送子弹
        player.fire(firing, shoot_sound, shots, all)

        # 创建新外星人
        if alienreload:
            # 每12 帧可能可能创建一个新外星人，是否能够创建由 ALIEN_ODDS 概率决定
            alienreload = alienreload - 1  # 减少重装计数器
        elif not int(random.random() * ALIEN_ODDS):  # 随机决定是否创建外星人
            # random.random() 生成一个 [0, 1) 范围内的随机浮点数
            # 乘以 ALIEN_ODDS (值为22)，得到 [0, 22) 范围内的随机数
            # int() 取整，得到 0 到 21 的整数
            # not 运算符将结果转换为布尔值：只有结果为 0 时，not 0 才为 True
            # 所以这个条件的意思是：每帧有 1/22 的概率创建新外星人。
            Alien(aliens, all, lastalien)  # 创建新外星人
            alienreload = ALIEN_RELOAD  # 重置重装计数器

        # 最新的一个外星人投掷炸弹
        if lastalien and not int(random.random() * BOMB_ODDS):  # 随机决定是否投掷炸弹
            Bomb(lastalien.sprite, all, bombs, all)  # 创建炸弹

        # 检测外星人和玩家的碰撞
        for alien in pg.sprite.spritecollide(player, aliens, 1):  # 碰撞检测（移除外星人）
            if pg.mixer and boom_sound is not None:  # 播放爆炸音效
                boom_sound.play()
            Explosion(alien, all)  # 创建外星人爆炸
            Explosion(player, all)  # 创建玩家爆炸
            score.incr()
            player.kill()  # 移除玩家

        # 检测子弹是否击中外星人
        for alien in pg.sprite.groupcollide(aliens, shots, 1, 1).keys():  # 组碰撞检测
            if pg.mixer and boom_sound is not None:  # 播放爆炸音效
                boom_sound.play()
            Explosion(alien, all)  # 创建爆炸效果
            score.incr()  # 增加分数

        # 检测外星人炸弹是否击中玩家
        for bomb in pg.sprite.spritecollide(player, bombs, 1):  # 炸弹碰撞检测
            if pg.mixer and boom_sound is not None:  # 播放爆炸音效
                boom_sound.play()
            Explosion(player, all)  # 创建玩家爆炸
            Explosion(bomb, all)  # 创建炸弹爆炸
            player.kill()  # 移除玩家

        # 绘制场景
        dirty = all.draw(screen)  # 绘制所有精灵，返回脏矩形区域
        pg.display.update(dirty)  # 只更新脏矩形区域

        # 将帧率限制在40fps，也称为40HZ或每秒40次
        clock.tick(40)

    # 等待1秒
    pg.time.wait(1000)

    # 退出游戏
    quit.quit_game()


# 如果运行此脚本，调用"main"函数
if __name__ == "__main__":
    main()  # 运行主函数
