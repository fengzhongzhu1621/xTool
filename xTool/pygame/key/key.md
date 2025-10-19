# pygame.QUIT
```python
# 游戏主循环
while running:
    # 处理事件
    # pygame.QUIT事件表示用户点击了关闭窗口按钮
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False  # 退出游戏循环
```

# pygame.KEYDOWN

```python
pygame.K_w # W键：向上移动
pygame.K_s # S键：向下移动
pygame.K_a # A键：向左移动
pygame.K_d # D键：向右移动
pygame.K_f
pygame.K_r
pygame.K_PLUS
pygame.K_MINUS
pygame.K_ESCAPE
pygame.K_1
pygame.K_2
pygame.K_3
pygame.K_4
pygame.K_5
pygame.K_6
pygame.K_7
pygame.K_8
pygame.K_9
```

```python
step = int(event.unicode)  # 将按键字符转换为数字
```

```python
while True:
    # 等待事件
    event = pygame.event.wait()
    if event.type == pygame.QUIT:  # 点击关闭按钮
        break
    if event.type == pygame.KEYDOWN:  # 按键事件
        if event.key == pygame.K_ESCAPE or event.unicode == "q":  # ESC或Q键退出
            break
```

```python
        going = True
        while going:
            events = pg.event.get()
            for e in events:
                # 退出条件：窗口关闭或ESC键
                if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
                    going = False
                # 处理数字键（0-9）切换相机
                if e.type == pg.KEYDOWN:
                    if e.key in range(pg.K_0, pg.K_0 + 10):
                        camera = self.init_cams(e.key - pg.K_0)  # 初始化指定索引的相机
```

```python
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
                        screen = display_screen.change_to_fullscreen()
                    else:
                        print("切换到窗口模式")
                        screen = display_screen.change_to_winscreen()
                    pg.display.flip()  # 更新显示
                    fullscreen = not fullscreen  # 切换全屏状态

        keystate = pg.key.get_pressed()  # 获取按键状态

```

# set_repeat()
```python
pg.key.set_repeat(500, 30)  # 设置按键重复：500ms延迟，30ms间隔

# 设置按键重复，以便按住键时可以连续滚动
old_k_delay, old_k_interval = pg.key.get_repeat()
pg.key.set_repeat(500, 30)  # 初始延迟500ms，重复间隔30ms
# 恢复原来的按键重复设置
pg.key.set_repeat(old_k_delay, old_k_interval)
```

# get_pressed()
```python
# 获取键盘按键状态
keystate = pygame.key.get_pressed()
# 根据WASD键控制圆形移动（y 轴向下）
if keystate[pygame.K_w]:  # W键：向上移动
    player_pos.y -= 300 * dt
if keystate[pygame.K_s]:  # S键：向下移动
    player_pos.y += 300 * dt
if keystate[pygame.K_a]:  # A键：向左移动
    player_pos.x -= 300 * dt
if keystate[pygame.K_d]:  # D键：向右移动
    player_pos.x += 300 * dt
```

keystate - 键盘状态字典，包含所有按键的按下状态（True/False）

## 计算移动方向

计算逻辑：

* keystate[pg.K_RIGHT] - 右键按下时为 True（值为1），否则为 False（值为0）
* keystate[pg.K_LEFT] - 左键按下时为 True（值为1），否则为 False（值为0）
* 通过减法运算得到方向值

结果分析：

* 右键按下：1 - 0 = 1 → 向右移动
* 左键按下：0 - 1 = -1 → 向左移动
* 两键都按下：1 - 1 = 0 → 停止移动
* 两键都未按下：0 - 0 = 0 → 停止移动

```python
direction = keystate[pg.K_RIGHT] - keystate[pg.K_LEFT]  # 计算移动方向
```

