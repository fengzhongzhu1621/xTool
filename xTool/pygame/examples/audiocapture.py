"""pygame.examples.audiocapture
Pygame 音频捕获示例

功能：
* 从麦克风录制声音
* 播放录制的声音
"""

import time

import pygame as pg
from pygame._sdl2 import AUDIO_ALLOW_FORMAT_CHANGE  # 允许音频格式更改
from pygame._sdl2 import AUDIO_F32  # 32位浮点音频格式
from pygame._sdl2 import AudioDevice  # 音频设备类
from pygame._sdl2 import get_audio_device_names  # 获取音频设备名称列表
from pygame._sdl2.mixer import set_post_mix  # 设置混音后回调函数

from xTool.pygame import init

# 初始化Pygame
# 预初始化混音器参数：采样率44100Hz，32位深度，2声道，512样本块大小
init.init_game(buffer=512)

# 获取可用的音频输入设备名称列表（True表示获取输入设备）
names = get_audio_device_names(True)
# 可用的音频输入设备: ['MacBook Pro麦克风']
print("可用的音频输入设备:", names)

sounds = []  # 存储声音对象的列表
sound_chunks = []  # 存储录制的音频数据块


def callback(audiodevice, audiomemoryview):
    """音频录制回调函数（在音频线程中调用）

    注意：实际获取的音频参数可能与请求的不完全一致
    """
    # print(type(audiomemoryview), len(audiomemoryview))
    # print(audiodevice)
    sound_chunks.append(bytes(audiomemoryview))  # 将音频数据转换为字节并保存


def postmix_callback(postmix, audiomemoryview):
    """混音后回调函数（在音频线程中调用）

    在混音过程结束时调用，用于处理混音后的音频数据
    """
    pass
    # print("postmix_callback: ", type(audiomemoryview), len(audiomemoryview), postmix)


# 设置混音后回调函数
set_post_mix(postmix_callback)

# 创建音频录制设备
audio = AudioDevice(
    devicename=names[0],  # 使用第一个音频输入设备
    iscapture=True,  # 设置为录制模式（输入设备）
    frequency=44100,  # 采样率：44100Hz
    audioformat=AUDIO_F32,  # 音频格式：32位浮点数
    numchannels=2,  # 声道数：立体声（2声道）
    chunksize=512,  # 每次处理的样本块大小
    allowed_changes=AUDIO_ALLOW_FORMAT_CHANGE,  # 允许音频格式自动调整
    callback=callback,  # 设置音频数据回调函数
)

# 开始录制（pause(0)表示取消暂停，开始录制）
audio.pause(0)

print("音频设备信息:", audio)
print(f"正在使用设备 '{names[0]}' 进行录制...")
time.sleep(5)  # 录制5秒钟


print("将录制的数据转换为pg.mixer.Sound对象")
# 将所有音频数据块合并并创建Sound对象
sound = pg.mixer.Sound(buffer=b"".join(sound_chunks))

print("播放录制的声音")
sound.play()  # 播放录制的声音

time.sleep(5)  # 等待播放完成
pg.quit()  # 退出Pygame
