# pygame.mixer
## pre_init()
```python
# Initialize pygame
if pg.get_sdl_version()[0] == 2:
    pg.mixer.pre_init(44100, 32, 2, 1024)
pg.init()
if pg.mixer and not pg.mixer.get_init():
    print("Warning, no sound")
    pg.mixer = None
```

## Sound()
```python
sound = pygame.mixer.Sound(file_path)  # 加载音效

print("将录制的数据转换为pg.mixer.Sound对象")
# 将所有音频数据块合并并创建Sound对象
sound = pg.mixer.Sound(buffer=b"".join(sound_chunks))

print("播放录制的声音")
sound.play()  # 播放录制的声音
```

# music
## load()
```python
music = os.path.join(resource_dir, "house_lo.wav")  # 背景音乐路径
pg.mixer.music.load(music)  # 加载背景音乐
pg.mixer.music.play(-1)  # 循环播放背景音乐
pg.mixer.music.load(file_path)  # 加载音频文件
```

## get_busy()
```python
# 主事件循环：当音乐正在播放或处于暂停状态时继续运行
while pg.mixer.music.get_busy() or paused:
```

## play()
```python
pg.mixer.music.play(-1)  # 循环播放背景音乐
pg.mixer.music.play(fade_ms=4000)
```

## set_volume()
```python
pg.mixer.music.set_volume(volume)
```

## set_endevent()
```python
pg.mixer.music.set_endevent(MUSIC_DONE)
```

## unpause()
```python 
pg.mixer.music.unpause()
```

## pause()
```python
pg.mixer.music.pause()
```

## rewind()
```python
pg.mixer.music.rewind()  # 倒带（仅支持特定格式）
```

## fadeout()
```python
pg.mixer.music.fadeout(5000)  # 在5秒内淡出音乐
```

## stop()
```python
pg.mixer.music.stop()  # 停止播放
```