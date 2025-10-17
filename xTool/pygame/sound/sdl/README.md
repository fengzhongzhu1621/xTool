# _sdl2
```python
from pygame._sdl2 import AUDIO_ALLOW_FORMAT_CHANGE  # 允许音频格式更改
from pygame._sdl2 import AUDIO_F32  # 32位浮点音频格式
from pygame._sdl2 import AudioDevice  # 音频设备类
from pygame._sdl2 import get_audio_device_names  # 获取音频设备名称列表
from pygame._sdl2.mixer import set_post_mix  # 设置混音后回调函数
```

## get_audio_device_names()
```python
# 获取可用的音频输入设备名称列表（True表示获取输入设备）
names = get_audio_device_names(True)
```

## set_post_mix()

```python
def postmix_callback(postmix, audiomemoryview):
    """混音后回调函数（在音频线程中调用）

    在混音过程结束时调用，用于处理混音后的音频数据
    """
    pass
    # print("postmix_callback: ", type(audiomemoryview), len(audiomemoryview), postmix)

# 设置混音后回调函数
set_post_mix(postmix_callback)
```

## AudioDevice()
```python
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
```
