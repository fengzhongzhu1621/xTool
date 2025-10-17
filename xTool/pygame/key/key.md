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
pygame.K_ESCAPE
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

# 鼠标
```python
while True:
    e = pg.event.wait()
    # Force application to only advance when main button is released
    if e.type == pg.MOUSEBUTTONUP and e.button == pg.BUTTON_LEFT:
        break
    elif e.type == pg.KEYDOWN and e.key == pg.K_s:
        pg.image.save(screen, name + ".png")
    elif e.type == pg.QUIT:
        pg.quit()
        raise SystemExit()
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

# 计算移动方向

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

