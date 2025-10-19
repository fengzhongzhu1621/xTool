"""pygame.examples.sound

播放声音文件并等待其播放完成。你需要pygame.mixer模块才能运行此示例。
注意在这个简单示例中，我们甚至不需要加载整个pygame包。
只需选择mixer用于声音和time用于延迟函数。

可选命令行参数：音频文件名
Playing a soundfile and waiting for it to finish. You'll need the
pygame.mixer module for this to work. Note how in this simple example
we don't even bother loading all of the pygame package.
Just pick the mixer for sound and time for the delay function.

Optional command line argument: audio file name
"""

import os
import sys

import pygame as pg

# 获取当前文件所在目录
main_dir = os.path.split(os.path.abspath(__file__))[0]


def main(file_path=None):
    """播放音频文件作为缓冲的声音样本
    Play an audio file as a buffered sound sample

    :param str file_path: 音频文件路径（默认为data/secosmic_low.wav）
    :param str file_path: audio file (default data/secosmic_low.wav)
    """
    # 选择所需的音频格式 - 初始化混音器，采样率为11025Hz
    # 如果初始化失败会抛出异常
    pg.mixer.init(11025)  # raises exception on fail

    # 加载声音文件
    sound = pg.mixer.Sound(file_path)

    # 开始播放声音
    print("播放声音中...")
    print("Playing Sound...")
    channel = sound.play()  # 返回播放通道对象

    # 轮询直到播放完成
    while channel.get_busy():  # 仍在播放中
        print("  ...仍在播放中...")
        print("  ...still going...")
        pg.time.wait(1000)  # 等待1秒

    print("...播放完成")
    print("...Finished")
    pg.quit()  # 退出pygame


if __name__ == "__main__":
    # 程序入口点
    if len(sys.argv) > 1:
        # 如果提供了命令行参数，使用指定的音频文件
        main(sys.argv[1])
    else:
        # 否则使用默认的音频文件
        main(os.path.join(main_dir, "data", "secosmic_lo.wav"))
