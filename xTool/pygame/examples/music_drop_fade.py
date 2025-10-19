"""pygame.examples.music_drop_fade
淡入播放音乐列表，同时观察多个事件

通过以下方法之一播放音乐文件时，会将音乐文件添加到播放列表：
- 从命令行传递的音乐文件会被播放
- 拖放到pygame窗口上的音乐文件和文件名会被播放
- 轮询剪贴板，如果找到音乐文件则播放

键盘控制：
* 按空格或回车键暂停音乐播放
* 按上或下方向键改变音乐音量
* 按左或右方向键在音轨中快进/快退5秒
* 按ESC键退出
* 按任何其他键跳到播放列表中的下一个音乐文件
"""

import os
import sys
from typing import List

import pygame as pg

VOLUME_CHANGE_AMOUNT = 0.02  # 上下方向键改变音量的速度


def add_file(filename):
    """
    添加文件到音乐文件列表

    此函数检查文件名是否存在且是音乐文件
    如果是，文件将被添加到音乐文件列表中（即使已经存在）
    类型检查基于文件扩展名，而不是文件内容
    我们只能在稍后使用mixer.music.load()时发现文件是否有效

    它会在文件目录及其data子目录中查找

    参数:
    filename - 要添加的文件名

    返回:
    如果文件成功添加返回True，否则返回False
    """
    if filename.rpartition(".")[2].lower() not in music_file_types:
        print(f"{filename} not added to file list")
        print("only these files types are allowed: ", music_file_types)
        return False
    elif os.path.exists(filename):  # 文件在当前目录存在
        music_file_list.append(filename)
    elif os.path.exists(os.path.join(main_dir, filename)):  # 文件在脚本目录存在
        music_file_list.append(os.path.join(main_dir, filename))
    elif os.path.exists(os.path.join(data_dir, filename)):  # 文件在data子目录存在
        music_file_list.append(os.path.join(data_dir, filename))
    else:
        print("file not found")
        return False
    print(f"{filename} added to file list")
    return True


def play_file(filename):
    """
    播放文件

    此函数调用add_file，如果成功则播放文件
    音乐将在前4秒内淡入
    set_endevent用于在歌曲结束时发布MUSIC_DONE事件
    当接收到MUSIC_DONE事件时，主循环将调用play_next()

    参数:
    filename - 要播放的文件名
    """
    global starting_pos

    if add_file(filename):
        try:  # 我们必须这样做，以防文件不是有效的音频文件
            pg.mixer.music.load(music_file_list[-1])  # 加载最新添加的文件
        except pg.error as e:
            print(e)  # 打印描述，例如'Not an Ogg Vorbis audio stream'
            if filename in music_file_list:
                music_file_list.remove(filename)
                print(f"{filename} removed from file list")
            return
        pg.mixer.music.play(fade_ms=4000)  # 淡入播放，持续4秒
        pg.mixer.music.set_volume(volume)  # 设置音量

        if filename.rpartition(".")[2].lower() in music_can_seek:
            print("file supports seeking")  # 文件支持搜索
            starting_pos = 0  # 设置起始位置为0
        else:
            print("file does not support seeking")  # 文件不支持搜索
            starting_pos = -1  # 设置起始位置为-1（不支持搜索）
        pg.mixer.music.set_endevent(MUSIC_DONE)  # 设置音乐结束事件


def play_next():
    """
    播放下一首歌曲

    此函数将播放music_file_list中的下一首歌曲
    它使用pop(0)获取下一首歌曲，然后将其附加到列表末尾
    歌曲将在前4秒内淡入
    """

    global starting_pos
    if len(music_file_list) > 1:
        nxt = music_file_list.pop(0)  # 获取并移除列表中的第一首歌曲

        try:
            pg.mixer.music.load(nxt)  # 加载歌曲
        except pg.error as e:
            print(e)
            print(f"{nxt} removed from file list")

        music_file_list.append(nxt)  # 将歌曲添加到列表末尾（循环播放）
        print("starting next song: ", nxt)
    else:
        nxt = music_file_list[0]  # 如果只有一首歌曲，直接播放
    pg.mixer.music.play(fade_ms=4000)  # 淡入播放
    pg.mixer.music.set_volume(volume)  # 设置音量
    pg.mixer.music.set_endevent(MUSIC_DONE)  # 设置结束事件

    if nxt.rpartition(".")[2].lower() in music_can_seek:
        starting_pos = 0  # 支持搜索的文件
    else:
        starting_pos = -1  # 不支持搜索的文件


def draw_text_line(text, y=0):
    """
    在显示表面上绘制一行文本

    文本将在给定的y位置水平居中
    文本的高度将添加到y并返回给调用者

    参数:
    text - 要绘制的文本
    y - 起始y坐标

    返回:
    下一行文本的y坐标
    """
    screen = pg.display.get_surface()  # 获取显示表面
    surf = font.render(text, 1, (255, 255, 255))  # 渲染文本为白色
    y += surf.get_height()  # 增加y坐标
    x = (screen.get_width() - surf.get_width()) / 2  # 计算水平居中位置
    screen.blit(surf, (x, y))  # 绘制文本
    return y  # 返回新的y坐标


def change_music_position(amount):
    """
    改变当前播放位置

    将当前播放位置改变amount秒
    这只适用于OGG和MP3文件
    music.get_pos()返回歌曲已播放的毫秒数，而不是文件中的当前位置
    我们必须自己跟踪起始位置
    music.set_pos()将以秒为单位设置位置

    参数:
    amount - 要改变的时间量（秒）
    """
    global starting_pos

    if starting_pos >= 0:  # 除非play_file()是OGG或MP3，否则将为-1
        played_for = pg.mixer.music.get_pos() / 1000.0  # 转换为秒
        old_pos = starting_pos + played_for  # 计算旧位置
        starting_pos = old_pos + amount  # 计算新起始位置
        pg.mixer.music.play(start=starting_pos)  # 从新位置开始播放
        print(f"jumped from {old_pos} to {starting_pos}")  # 打印跳转信息


MUSIC_DONE = pg.event.custom_type()  # 设置为mixer.music.set_endevent()的事件
main_dir = os.path.split(os.path.abspath(__file__))[0]  # 主目录路径
data_dir = os.path.join(main_dir, "data")  # 数据目录路径

starting_pos = 0  # 用于快进和快退的起始位置
volume = 0.75  # 初始音量
music_file_list: List[str] = []  # 音乐文件列表
music_file_types = ("mp3", "ogg", "mid", "mod", "it", "xm", "wav")  # 支持的音乐文件类型
music_can_seek = ("mp3", "ogg", "mod", "it", "xm")  # 支持搜索的音乐文件类型


def main() -> None:
    # 初始化阶段
    global font, volume  # 声明全局变量

    running = True  # 主循环控制标志
    paused = False  # 暂停状态标志
    change_volume = 0  # 音量变化量（按键持续改变）

    # Pygame 系统初始化
    pg.init()  # 初始化所有Pygame模块
    pg.display.set_mode((640, 480))  # 创建640x480像素的窗口
    font = pg.font.SysFont("Arial", 24)  # 创建24号Arial字体
    clock = pg.time.Clock()  # 创建时钟对象用于控制帧率

    # 剪贴板监控初始化
    pg.scrap.init()  # 初始化剪贴板功能
    pg.SCRAP_TEXT = pg.scrap.get_types()[0]  # 获取剪贴板文本类型
    scrap_get = pg.scrap.get(pg.SCRAP_TEXT)  # 获取当前剪贴板内容
    clipped = "" if scrap_get is None else scrap_get.decode("UTF-8")  # 解码为字符串

    # add the command line arguments to the  music_file_list
    for arg in sys.argv[1:]:
        add_file(arg)

    # 播放默认音乐
    play_file("house_lo.ogg")  # 播放Pygame自带的示例音乐

    # 在屏幕上绘制操作说明
    y = draw_text_line("Drop music files or path names onto this window", 20)
    y = draw_text_line("Copy file names into the clipboard", y)
    y = draw_text_line("Or feed them from the command line", y)
    y = draw_text_line("If it's music it will play!", y)
    y = draw_text_line("SPACE to pause or UP/DOWN to change volume", y)
    y = draw_text_line("LEFT and RIGHT will skip around the track", y)
    draw_text_line("Other keys will start the next track", y)

    """
    This is the main loop
    It will respond to drag and drop, clipboard changes, and key presses
    """
    while running:
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                running = False
            elif ev.type == pg.DROPTEXT:  # 拖放文本（文件路径）
                play_file(ev.text)
            elif ev.type == pg.DROPFILE:  # 直接拖放文件
                play_file(ev.file)
            elif ev.type == MUSIC_DONE:  # 当前歌曲播放完成
                play_next()  # 自动播放下一首
            elif ev.type == pg.KEYDOWN:
                if ev.key == pg.K_ESCAPE:
                    running = False  # exit loop
                elif ev.key in (pg.K_SPACE, pg.K_RETURN):
                    if paused:
                        pg.mixer.music.unpause()
                        paused = False
                    else:
                        pg.mixer.music.pause()
                        paused = True
                elif ev.key == pg.K_UP:  # 上键 - 增加音量
                    change_volume = VOLUME_CHANGE_AMOUNT
                elif ev.key == pg.K_DOWN:  # 下键 - 减小音量
                    change_volume = -VOLUME_CHANGE_AMOUNT
                elif ev.key == pg.K_RIGHT:  # 右键 - 快进5秒
                    change_music_position(+5)
                elif ev.key == pg.K_LEFT:  # 左键 - 快退5秒
                    change_music_position(-5)

                else:  # 其他任意键 - 播放下一首
                    play_next()

            elif ev.type == pg.KEYUP:
                if ev.key in (pg.K_UP, pg.K_DOWN):
                    change_volume = 0

        # 音量持续调整
        if change_volume:  # 如果用户按住音量键
            volume += change_volume  # 持续改变音量
            volume = min(max(0, volume), 1)  # 限制音量在0-1范围内
            pg.mixer.music.set_volume(volume)  # 应用新音量
            print("volume:", volume)  # 控制台输出当前音量

        # 检查剪贴板是否发生变化
        scrap_get = pg.scrap.get(pg.SCRAP_TEXT)
        new_text = "" if scrap_get is None else scrap_get.decode("UTF-8")

        if new_text != clipped:  # 如果剪贴板内容发生变化
            clipped = new_text  # 更新保存的内容
            play_file(clipped)  # 尝试播放新文件

        pg.display.flip()
        clock.tick(9)  # keep CPU use down by updating screen less often

    pg.quit()


if __name__ == "__main__":
    main()
