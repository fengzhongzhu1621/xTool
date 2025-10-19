"""pygame.examples.sound_array_demos

在任意Sound对象上创建回声效果。
Creates an echo effect on any Sound object.

使用sndarray和numpy创建原始声音的偏移衰减副本。
目前使用硬编码值设置回声数量和延迟，便于根据需要重新创建。
Uses sndarray and numpy to create offset faded copies of the
original sound. Currently it just uses hardcoded values for the
number of echos and the delay. Easy for you to recreate as
needed.

版本2的变更：
version 2. changes:
- 现在应该适用于不同的采样率
- Should work with different sample rates now.
- 封装成函数
- put into a function.
- 默认使用numpy，但回退到Numeric
- Uses numpy by default, but falls back on Numeric.
"""

import os
import time

import pygame as pg
from numpy import int16, int32, zeros

# 初始化混音器 - 使用默认参数
# pg.mixer.init(44100, -16, 0)  # 44.1kHz采样率，16位有符号，单声道
pg.mixer.init()  # 使用默认设置初始化混音器
# pg.mixer.init(11025, -16, 0)  # 11.025kHz采样率
# pg.mixer.init(11025)  # 11.025kHz采样率，默认格式


def make_echo(sound, samples_per_second, mydebug=True):
    """返回一个带有回声效果的声音
    returns a sound which is echoed of the last one.

    :param sound: 原始声音对象
    :param samples_per_second: 每秒采样数（采样率）
    :param mydebug: 是否启用调试输出
    :return: 带有回声效果的新声音对象
    """

    echo_length = 3.5  # 回声持续时间（秒）

    # 将声音转换为numpy数组
    a1 = pg.sndarray.array(sound)
    if mydebug:
        print(f"原始声音数组形状: {a1.shape}")
        print(f"SHAPE1: {a1.shape}")

    length = a1.shape[0]  # 原始声音的采样点数量

    # 创建用于存储回声的数组
    # myarr = zeros(length+12000)  # 旧方法
    myarr = zeros(a1.shape, int32)  # 创建与原始声音相同形状的数组

    # 根据声音的维度（单声道/立体声）计算新数组的大小
    if len(a1.shape) > 1:
        # 立体声：两个声道
        # mult = a1.shape[1]  # 声道数量
        size = (a1.shape[0] + int(echo_length * a1.shape[0]), a1.shape[1])
        # size = (a1.shape[0] + int(a1.shape[0] + (echo_length * 3000)), a1.shape[1])
    else:
        # 单声道
        # mult = 1
        size = (a1.shape[0] + int(echo_length * a1.shape[0]),)
        # size = (a1.shape[0] + int(a1.shape[0] + (echo_length * 3000)),)

    if mydebug:
        print(f"回声部分长度: {int(echo_length * a1.shape[0])}")
        print(int(echo_length * a1.shape[0]))

    # 创建足够大的数组来容纳原始声音和回声
    myarr = zeros(size, int32)

    if mydebug:
        print(f"新数组大小: {size}")
        print(f"size {size}")
        print(f"新数组形状: {myarr.shape}")
        print(myarr.shape)

    # 将原始声音复制到新数组的开头
    myarr[:length] = a1

    # 调试用的注释代码
    # print(myarr[3000:length+3000])
    # print(a1 >> 1)
    # print("a1.shape %s" % (a1.shape,))
    # c = myarr[3000:length+(3000*mult)]
    # print("c.shape %s" % (c.shape,))

    # 计算回声间隔（采样点数量）
    incr = int(samples_per_second / echo_length)  # 每个回声之间的间隔
    gap = length  # 原始声音的长度

    # 添加4个逐渐衰减的回声
    # 每个回声向右偏移，音量逐渐减半
    myarr[incr : gap + incr] += a1 >> 1  # 第一个回声，音量减半
    myarr[incr * 2 : gap + (incr * 2)] += a1 >> 2  # 第二个回声，音量减为1/4
    myarr[incr * 3 : gap + (incr * 3)] += a1 >> 3  # 第三个回声，音量减为1/8
    myarr[incr * 4 : gap + (incr * 4)] += a1 >> 4  # 第四个回声，音量减为1/16

    if mydebug:
        print(f"处理后数组形状: {myarr.shape}")
        print(f"SHAPE2: {myarr.shape}")

    # 将数组转换回声音对象（转换为16位有符号整数）
    sound2 = pg.sndarray.make_sound(myarr.astype(int16))

    return sound2


def slow_down_sound(sound, rate):
    """返回原始声音的慢速版本
    returns a sound which is a slowed down version of the original.

    :param sound: 原始声音对象
    :param rate: 声音减慢的速率，例如0.5表示半速
    rate - at which the sound should be slowed down.  eg. 0.5 would be half speed.
    :return: 慢速版本的声音对象
    """

    raise NotImplementedError("此功能尚未实现")

    # 以下是被注释掉的实验性代码
    # grow_rate = 1 / rate  # 增长速率
    # make it 1/rate times longer.  # 使声音变为1/rate倍长

    # 将声音转换为数组
    # a1 = pg.sndarray.array(sound)

    # 尝试将声音数组转换为表面进行缩放（实验性方法）
    # surf = pg.surfarray.make_surface(a1)
    # print(a1.shape[0] * grow_rate)
    # scaled_surf = pg.transform.scale(surf, (int(a1.shape[0] * grow_rate), a1.shape[1]))
    # print(scaled_surf)
    # print(surf)

    # 另一种尝试：直接缩放数组
    # a2 = a1 * rate
    # print(a1.shape)
    # print(a2.shape)
    # print(a2)
    # sound2 = pg.sndarray.make_sound(a2.astype(int16))
    # return sound2


def sound_from_pos(sound, start_pos, samples_per_second=None, inplace=1):
    """返回从指定位置开始的声音
    returns a sound which begins at the start_pos.

    :param sound: 原始声音对象
    :param start_pos: 开始位置（从开头算起的秒数）
    start_pos - in seconds from the beginning.
    :param samples_per_second: 每秒采样数（采样率），如果为None则从混音器获取
    samples_per_second -
    :param inplace: 是否重用声音数据（1=True，0=False）
    :return: 从指定位置开始的新声音对象
    """

    # 检查是否要重用声音数据
    # see if we want to reuse the sound data or not.
    if inplace:
        # 使用samples()方法获取声音样本（原地操作，可能更快）
        a1 = pg.sndarray.samples(sound)
    else:
        # 使用array()方法创建声音数组的副本
        a1 = pg.sndarray.array(sound)

    # 检查是否提供了每秒采样数，如果没有则查询混音器
    # see if samples per second has been given.  If not, query the pg.mixer.
    #   eg. it might be set to 22050
    if samples_per_second is None:
        # 从混音器获取采样率（get_init()返回(频率, 格式, 声道数)）
        samples_per_second = pg.mixer.get_init()[0]

    # 计算开始位置的采样点索引
    # figure out the start position in terms of samples.
    start_pos_in_samples = int(start_pos * samples_per_second)

    # 从开始位置截断声音的开头部分
    # cut the beginning off the sound at the start position.
    a2 = a1[start_pos_in_samples:]

    # 从数组创建新的声音实例
    # make the Sound instance from the array.
    sound2 = pg.sndarray.make_sound(a2)

    return sound2


def main() -> None:
    """播放各种sndarray效果
    play various sndarray effects
    """

    # 获取当前文件所在目录
    main_dir = os.path.split(os.path.abspath(__file__))[0]
    print(f"混音器初始化参数: {pg.mixer.get_init()}")
    print(f"mixer.get_init {pg.mixer.get_init()}")

    # 获取采样率
    samples_per_second = pg.mixer.get_init()[0]

    print(("-" * 30) + "\n")
    print("加载声音文件")
    print("loading sound")
    # 加载车门关闭声音
    sound = pg.mixer.Sound(os.path.join(main_dir, "data", "car_door.wav"))

    print("-" * 30)
    print("测试从指定位置开始播放")
    print("start positions")
    print("-" * 30)

    # 测试从0.1秒位置开始播放
    start_pos = 0.1
    sound2 = sound_from_pos(sound, start_pos, samples_per_second)

    print(f"原始声音长度: {sound.get_length()}秒")
    print(f"sound.get_length {sound.get_length()}")
    print(f"截取后声音长度: {sound2.get_length()}秒")
    print(f"sound2.get_length {sound2.get_length()}")

    # 播放截取的声音
    sound2.play()
    while pg.mixer.get_busy():
        pg.time.wait(200)  # 等待200毫秒

    print("等待2秒")
    print("waiting 2 seconds")
    pg.time.wait(2000)
    print("播放原始声音")
    print("playing original sound")

    # 播放原始声音
    sound.play()
    while pg.mixer.get_busy():
        pg.time.wait(200)

    print("等待2秒")
    print("waiting 2 seconds")
    pg.time.wait(2000)

    # 被注释掉的慢速声音功能（尚未实现）
    # if 0:
    #    #TODO: this is broken.
    #    print(("-" * 30) + "\n")
    #    print("Slow down the original sound.")
    #    rate = 0.2
    #    slowed_sound = slow_down_sound(sound, rate)
    #    slowed_sound.play()
    #    while pg.mixer.get_busy():
    #        pg.time.wait(200)

    print("-" * 30)
    print("测试回声效果")
    print("echoing")
    print("-" * 30)

    # 测试回声效果
    t1 = time.time()
    sound2 = make_echo(sound, samples_per_second)
    print(f"创建回声耗时: {time.time() - t1}秒")
    print("time to make echo %i" % (time.time() - t1,))

    print("播放原始声音")
    print("original sound")
    sound.play()
    while pg.mixer.get_busy():
        pg.time.wait(200)

    print("播放回声声音")
    print("echoed sound")
    sound2.play()
    while pg.mixer.get_busy():
        pg.time.wait(200)

    # 加载另一个声音文件测试回声效果
    sound = pg.mixer.Sound(os.path.join(main_dir, "data", "secosmic_lo.wav"))

    t1 = time.time()
    sound3 = make_echo(sound, samples_per_second)
    print(f"创建第二个回声耗时: {time.time() - t1}秒")
    print("time to make echo %i" % (time.time() - t1,))

    print("播放原始声音")
    print("original sound")
    sound.play()
    while pg.mixer.get_busy():
        pg.time.wait(200)

    print("播放回声声音")
    print("echoed sound")
    sound3.play()
    while pg.mixer.get_busy():
        pg.time.wait(200)

    pg.quit()  # 退出pygame


if __name__ == "__main__":
    main()
