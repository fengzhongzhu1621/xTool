

# set_visible()
```python
pg.mouse.set_visible(0)  # 隐藏鼠标光标
```

# get_pos
```python
pos = pg.mouse.get_pos()  # 获取鼠标当前位置
mouse_x, mouse_y = pg.mouse.get_pos()  # 获取鼠标当前位置
```

# get_pressed()
```python
# 检查按钮是否被点击并切换光标
if button.collidepoint(mouse_x, mouse_y):  # 鼠标在按钮上
    button = pg.draw.rect(
        bg,
        (60, 100, 255),  # 悬停颜色（深蓝色）
        (
            139,
            300,
            button_text.get_width() + 5,
            button_text.get_height() + 50,
        ),
    )
    bg.blit(button_text, button_text_rect)

    # 检测鼠标点击（防止连续触发）
    if pg.mouse.get_pressed()[0] == 1 and pressed is False:  # 左键按下且之前未按下
        button = pg.draw.rect(
            bg,
            (0, 0, 139),  # 点击颜色（深蓝色）
            (
                139,
                300,
                button_text.get_width() + 5,
                button_text.get_height() + 50,
            ),
        )
        bg.blit(button_text, button_text_rect)
        index += 1  # 切换到下一个光标
        index %= len(cursors)  # 循环索引
        pg.mouse.set_cursor(cursors[index])  # 设置新光标
        pg.display.update()  # 更新显示
        pg.time.delay(40)  # 短暂延迟防止连续点击

# 更新鼠标按下状态
if pg.mouse.get_pressed()[0] == 1:
    pressed = True  # 鼠标按下
elif pg.mouse.get_pressed()[0] == 0:
    pressed = False  # 鼠标释放

# 处理事件
for event in pg.event.get():
    if event.type == pg.QUIT:  # 窗口关闭事件
        pg.quit()  # 退出Pygame
        raise SystemExit  # 退出程序

pg.display.update()  # 更新显示
```

# 鼠标事件
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

```python
# 处理输入事件
for event in pg.event.get():
    if event.type == pg.QUIT:  # 窗口关闭事件
        going = False
    elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:  # ESC键退出
        going = False
    elif event.type == pg.MOUSEBUTTONDOWN:  # 鼠标按下事件
        if fist.punch(chimp):  # 如果击中猩猩
            punch_sound.play()  # 播放击中音效
            chimp.punched()  # 触发猩猩旋转
        else:
            whiff_sound.play()  # 播放挥空音效
    elif event.type == pg.MOUSEBUTTONUP:  # 鼠标释放事件
        fist.unpunch()  # 收回拳头
```