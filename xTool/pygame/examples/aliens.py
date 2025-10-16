#!/usr/bin/env python
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
from typing import List

# import basic pygame modules
import pygame as pg

from xTool.pygame.image import load_image

# see if we can load more than standard BMP
if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")


# 游戏常量
MAX_SHOTS = 2  # 屏幕上最多允许的玩家子弹数量
ALIEN_ODDS = 22  # 新外星人出现的概率（1/22）
BOMB_ODDS = 60  # 新炸弹掉落的概率（1/60）
ALIEN_RELOAD = 12  # 新外星人出现的帧间隔
SCREENRECT = pg.Rect(0, 0, 640, 480)  # 屏幕矩形区域
g_score = 0  # 游戏分数

main_dir = os.path.split(os.path.abspath(__file__))[0]
resource_dir = os.path.join(main_dir, "data")


def load_sound(file):
    """加载音效（因为pygame可能在没有mixer的情况下编译）"""
    if not pg.mixer:
        return None
    file = os.path.join(main_dir, "data", file)  # 构建完整文件路径
    try:
        sound = pg.mixer.Sound(file)  # 加载音效
        return sound
    except pg.error:
        print(f"警告，无法加载 {file}")
    return None


# Each type of game object gets an init and an update function.
# The update function is called once per frame, and it is when each object should
# change its current position and state.
#
# The Player object actually gets a "move" function instead of update,
# since it is passed extra information about the keyboard.


class Player(pg.sprite.Sprite):
    """代表玩家的月球车类型汽车"""

    speed = 10  # 移动速度
    bounce = 24  # 弹跳效果参数
    gun_offset = -11  # 枪口偏移量
    images: List[pg.Surface] = []  # 玩家图像列表

    def __init__(self, *groups):
        pg.sprite.Sprite.__init__(self, *groups)  # 调用父类构造函数
        self.image = self.images[0]  # 设置初始图像
        # 将玩家放置在屏幕底部中央
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.reloading = 0  # 重装状态
        self.origtop = self.rect.top  # 原始顶部位置
        self.facing = -1  # 面向方向（-1左，1右）

    def move(self, direction):
        """移动玩家"""
        if direction:
            self.facing = direction  # 更新面向方向
        # 根据方向移动玩家
        self.rect.move_ip(direction * self.speed, 0)
        # 确保玩家不会移出屏幕
        self.rect = self.rect.clamp(SCREENRECT)
        # 根据移动方向切换图像（左右镜像）
        if direction < 0:
            self.image = self.images[0]  # 向左的图像
        elif direction > 0:
            self.image = self.images[1]  # 向右的图像
        # 添加弹跳效果
        self.rect.top = self.origtop - (self.rect.left // self.bounce % 2)

    def gunpos(self):
        """获取枪口位置"""
        pos = self.facing * self.gun_offset + self.rect.centerx
        return pos, self.rect.top


class Alien(pg.sprite.Sprite):
    """外星人飞船，缓慢在屏幕上移动"""

    speed = 13  # 移动速度
    animcycle = 12  # 动画循环帧数
    images: List[pg.Surface] = []  # 外星人图像列表

    def __init__(self, *groups):
        pg.sprite.Sprite.__init__(self, *groups)  # 调用父类构造函数
        self.image = self.images[0]  # 设置初始图像
        self.rect = self.image.get_rect()  # 获取矩形区域
        # 随机选择移动方向
        self.facing = random.choice((-1, 1)) * Alien.speed
        self.frame = 0  # 动画帧计数器
        # 如果向左移动，从屏幕右侧开始
        if self.facing < 0:
            self.rect.right = SCREENRECT.right

    def update(self, *args, **kwargs):
        """更新外星人状态"""
        # 移动外星人
        self.rect.move_ip(self.facing, 0)
        # 如果碰到屏幕边缘，改变方向并下移一行
        if not SCREENRECT.contains(self.rect):
            self.facing = -self.facing  # 反向移动
            self.rect.top = self.rect.bottom + 1  # 下移一行
            self.rect = self.rect.clamp(SCREENRECT)  # 确保在屏幕内
        # 更新动画帧
        self.frame = self.frame + 1
        # 循环播放3帧动画
        self.image = self.images[self.frame // self.animcycle % 3]


class Explosion(pg.sprite.Sprite):
    """An explosion. Hopefully the Alien and not the player!"""

    defaultlife = 12
    animcycle = 3
    images: List[pg.Surface] = []

    def __init__(self, actor, *groups):
        pg.sprite.Sprite.__init__(self, *groups)
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=actor.rect.center)
        self.life = self.defaultlife

    def update(self, *args, **kwargs):
        """Called every time around the game loop.

        Show the explosion surface for 'defaultlife'.
        Every game tick(update), we decrease the 'life'.

        Also we animate the explosion.
        """
        self.life = self.life - 1
        self.image = self.images[self.life // self.animcycle % 2]
        if self.life <= 0:
            self.kill()


class Shot(pg.sprite.Sprite):
    """玩家发射的子弹"""

    speed = -11  # 子弹速度（向上）
    images: List[pg.Surface] = []  # 子弹图像列表

    def __init__(self, pos, *groups):
        pg.sprite.Sprite.__init__(self, *groups)  # 调用父类构造函数
        self.image = self.images[0]  # 设置子弹图像
        self.rect = self.image.get_rect(midbottom=pos)  # 设置初始位置

    def update(self, *args, **kwargs):
        """每帧更新子弹状态

        每个tick我们向上移动子弹
        """
        self.rect.move_ip(0, self.speed)  # 向上移动
        if self.rect.top <= 0:  # 如果子弹飞出屏幕顶部
            self.kill()  # 移除子弹


class Bomb(pg.sprite.Sprite):
    """外星人投掷的炸弹"""

    speed = 9  # 炸弹下落速度
    images: List[pg.Surface] = []  # 炸弹图像列表

    def __init__(self, alien, explosion_group, *groups):
        pg.sprite.Sprite.__init__(self, *groups)  # 调用父类构造函数
        self.image = self.images[0]  # 设置炸弹图像
        # 在外星人下方5像素位置创建炸弹
        self.rect = self.image.get_rect(midbottom=alien.rect.move(0, 5).midbottom)
        self.explosion_group = explosion_group  # 爆炸效果组

    def update(self, *args, **kwargs):
        """每帧更新炸弹状态

        每帧我们将精灵'rect'向下移动
        当它到达底部时：

        - 创建爆炸效果
        - 移除炸弹
        """
        self.rect.move_ip(0, self.speed)  # 向下移动
        if self.rect.bottom >= 470:  # 如果炸弹到达屏幕底部
            Explosion(self, self.explosion_group)  # 创建爆炸效果
            self.kill()  # 移除炸弹


class Score(pg.sprite.Sprite):
    """用于跟踪分数"""

    def __init__(self, *groups):
        pg.sprite.Sprite.__init__(self, *groups)  # 调用父类构造函数
        self.font = pg.font.Font(None, 20)  # 创建字体
        self.font.set_italic(1)  # 设置斜体
        self.color = "white"  # 分数颜色
        self.lastscore = -1  # 上一次分数
        self.update()  # 初始更新
        self.rect = self.image.get_rect().move(10, 450)  # 设置显示位置

    def update(self, *args, **kwargs):
        """只有当分数发生变化时才更新"""
        if g_score != self.lastscore:  # 如果分数有变化
            self.lastscore = g_score  # 更新上一次分数
            msg = f"分数: {g_score}"  # 创建分数文本
            self.image = self.font.render(msg, 0, self.color)  # 渲染分数图像


def main(winstyle=0):
    """游戏主函数"""
    # 初始化pygame
    if pg.get_sdl_version()[0] == 2:
        pg.mixer.pre_init(44100, 32, 2, 1024)  # SDL2音频预初始化
    pg.init()  # 初始化pygame
    if pg.mixer and not pg.mixer.get_init():  # 检查音频是否初始化成功
        print("警告，没有声音")
        pg.mixer = None

    fullscreen = False  # 全屏状态
    # 设置显示模式
    winstyle = 0  # 窗口模式
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)  # 获取最佳颜色深度
    screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)  # 创建显示窗口

    # 加载图像，分配给精灵类
    # （在类使用之前执行，在屏幕设置之后）
    img = load_image(os.path.join(resource_dir, "player1.gif"))
    Player.images = [img, pg.transform.flip(img, 1, 0)]  # 玩家左右图像
    img = load_image(os.path.join(resource_dir, "explosion1.gif"))
    Explosion.images = [img, pg.transform.flip(img, 1, 1)]  # 爆炸图像
    Alien.images = [
        load_image(os.path.join(resource_dir, im)) for im in ("alien1.gif", "alien2.gif", "alien3.gif")
    ]  # 外星人动画图像
    Bomb.images = [load_image(os.path.join(resource_dir, "bomb.gif"))]  # 炸弹图像
    Shot.images = [load_image(os.path.join(resource_dir, "shot.gif"))]  # 子弹图像

    # 装饰游戏窗口
    icon = pg.transform.scale(Alien.images[0], (32, 32))  # 创建窗口图标
    pg.display.set_icon(icon)  # 设置窗口图标
    pg.display.set_caption("Pygame Aliens")  # 设置窗口标题
    pg.mouse.set_visible(0)  # 隐藏鼠标光标

    # 创建背景，平铺背景图像
    bgdtile = load_image("background.gif")  # 加载背景瓦片
    background = pg.Surface(SCREENRECT.size)  # 创建背景表面
    # 平铺背景图像
    for x in range(0, SCREENRECT.width, bgdtile.get_width()):
        background.blit(bgdtile, (x, 0))
    screen.blit(background, (0, 0))  # 绘制背景到屏幕
    pg.display.flip()  # 更新显示

    # 加载音效
    boom_sound = load_sound("boom.wav")  # 爆炸音效
    shoot_sound = load_sound("car_door.wav")  # 射击音效
    if pg.mixer:
        music = os.path.join(main_dir, "data", "house_lo.wav")  # 背景音乐路径
        pg.mixer.music.load(music)  # 加载背景音乐
        pg.mixer.music.play(-1)  # 循环播放背景音乐

    # 初始化游戏组
    aliens = pg.sprite.Group()  # 外星人组
    shots = pg.sprite.Group()  # 子弹组
    bombs = pg.sprite.Group()  # 炸弹组
    all = pg.sprite.RenderUpdates()  # 所有需要更新的精灵组
    lastalien = pg.sprite.GroupSingle()  # 最后一个外星人（用于投掷炸弹）

    # 创建一些初始值
    alienreload = ALIEN_RELOAD  # 外星人重装计数器
    clock = pg.time.Clock()  # 游戏时钟

    # 初始化起始精灵
    global g_score
    player = Player(all)  # 创建玩家
    Alien(aliens, all, lastalien)  # 创建初始外星人
    if pg.font:
        all.add(Score(all))  # 添加分数显示

    # 当玩家存活时运行主循环
    while player.alive():
        # 获取输入
        for event in pg.event.get():
            if event.type == pg.QUIT:  # 退出事件
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:  # ESC键退出
                return
            if event.type == pg.KEYDOWN:  # 按键事件
                if event.key == pg.K_f:  # f键切换全屏
                    if not fullscreen:
                        print("切换到全屏模式")
                        screen_backup = screen.copy()  # 备份屏幕内容
                        screen = pg.display.set_mode(SCREENRECT.size, winstyle | pg.FULLSCREEN, bestdepth)  # 切换到全屏
                        screen.blit(screen_backup, (0, 0))  # 恢复屏幕内容
                    else:
                        print("切换到窗口模式")
                        screen_backup = screen.copy()  # 备份屏幕内容
                        screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)  # 切换到窗口模式
                        screen.blit(screen_backup, (0, 0))  # 恢复屏幕内容
                    pg.display.flip()  # 更新显示
                    fullscreen = not fullscreen  # 切换全屏状态

        keystate = pg.key.get_pressed()  # 获取按键状态

        # 清除/擦除上次绘制的精灵
        all.clear(screen, background)

        # 更新所有精灵
        all.update()

        # 处理玩家输入
        direction = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]  # 计算移动方向
        player.move(direction)  # 移动玩家
        firing = keystate[pg.K_SPACE]  # 射击状态
        # 如果不在重装状态、正在射击且子弹数量未达上限
        if not player.reloading and firing and len(shots) < MAX_SHOTS:
            Shot(player.gunpos(), shots, all)  # 创建子弹
            if pg.mixer and shoot_sound is not None:  # 播放射击音效
                shoot_sound.play()
        player.reloading = firing  # 更新重装状态

        # 创建新外星人
        if alienreload:
            alienreload = alienreload - 1  # 减少重装计数器
        elif not int(random.random() * ALIEN_ODDS):  # 随机决定是否创建外星人
            Alien(aliens, all, lastalien)  # 创建新外星人
            alienreload = ALIEN_RELOAD  # 重置重装计数器

        # 投掷炸弹
        if lastalien and not int(random.random() * BOMB_ODDS):  # 随机决定是否投掷炸弹
            Bomb(lastalien.sprite, all, bombs, all)  # 创建炸弹

        # 检测外星人和玩家的碰撞
        for alien in pg.sprite.spritecollide(player, aliens, 1):  # 碰撞检测（移除外星人）
            if pg.mixer and boom_sound is not None:  # 播放爆炸音效
                boom_sound.play()
            Explosion(alien, all)  # 创建外星人爆炸
            Explosion(player, all)  # 创建玩家爆炸
            g_score = g_score + 1  # 增加分数
            player.kill()  # 移除玩家

        # 检测子弹是否击中外星人
        for alien in pg.sprite.groupcollide(aliens, shots, 1, 1).keys():  # 组碰撞检测
            if pg.mixer and boom_sound is not None:  # 播放爆炸音效
                boom_sound.play()
            Explosion(alien, all)  # 创建爆炸效果
            g_score = g_score + 1  # 增加分数

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

    # 游戏结束处理
    if pg.mixer:
        pg.mixer.music.fadeout(1000)  # 背景音乐淡出
    pg.time.wait(1000)  # 等待1秒


# 如果运行此脚本，调用"main"函数
if __name__ == "__main__":
    main()  # 运行主函数
    pg.quit()  # 退出pygame
