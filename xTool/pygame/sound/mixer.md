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
```

# music
## load()
```python
music = os.path.join(resource_dir, "house_lo.wav")  # 背景音乐路径
pg.mixer.music.load(music)  # 加载背景音乐
pg.mixer.music.play(-1)  # 循环播放背景音乐
```

## play()
```python
pg.mixer.music.play(-1)  # 循环播放背景音乐
```
