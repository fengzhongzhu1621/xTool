

# set_visible()
```python
pg.mouse.set_visible(0)  # 隐藏鼠标光标
```

# get_visible()
```python
pg.mouse.get_visible()
```

# get_pos()
```python
pos = pg.mouse.get_pos()  # 获取鼠标当前位置
mouse_x, mouse_y = pg.mouse.get_pos()  # 获取鼠标当前位置
```

# get_rel()
```python
rel = pg.mouse.get_rel()  # 获取鼠标相对移动量
virtual_x += rel[0]  # 累计虚拟鼠标X坐标
virtual_y += rel[1]  # 累计虚拟鼠标Y坐标
```

# get_grab()
```python
# 虚拟鼠标状态（当输入抓取且鼠标不可见时）
is_virtual_mouse = pg.event.get_grab() and not pg.mouse.get_visible()
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

# 拖拽事件
```python
# 主事件循环
while going:
    # 处理事件队列
    for ev in pg.event.get():
        if ev.type == pg.QUIT:  # 窗口关闭事件
            going = False  # 退出循环
        elif ev.type == pg.DROPBEGIN:  # 拖放开始事件
            print(ev)  # 打印事件对象
            print("文件拖放开始!")
        elif ev.type == pg.DROPCOMPLETE:  # 拖放完成事件
            print(ev)  # 打印事件对象
            print("文件拖放完成!")
        elif ev.type == pg.DROPTEXT:  # 拖放文本事件
            print(ev)  # 打印事件对象
            # 更新显示文本为拖放的文本内容
            spr_file_text = font.render(ev.text, 1, (255, 255, 255))
            spr_file_text_rect = spr_file_text.get_rect()
            spr_file_text_rect.center = surf.get_rect().center  # 文本居中
        elif ev.type == pg.DROPFILE:  # 拖放文件事件
            print(ev)  # 打印事件对象
            # 更新显示文本为文件路径
            spr_file_text = font.render(ev.file, 1, (255, 255, 255))
            spr_file_text_rect = spr_file_text.get_rect()
            spr_file_text_rect.center = surf.get_rect().center  # 文本居中

            # 尝试打开文件，如果是图像文件则加载显示
            filetype = ev.file[-3:]  # 获取文件扩展名（后3个字符）
            if filetype in ["png", "bmp", "jpg"]:  # 检查是否为支持的图像格式
                spr_file_image = pg.image.load(ev.file).convert()  # 加载并转换图像
                spr_file_image.set_alpha(127)  # 设置半透明效果（alpha值127）
                spr_file_image_rect = spr_file_image.get_rect()  # 获取图像矩形区域
                spr_file_image_rect.center = surf.get_rect().center  # 图像居中显示
```

```python
while going:
    # 处理事件队列
    for e in pg.event.get():
        if e.type == pg.KEYDOWN:  # 按键事件
            if e.key == pg.K_ESCAPE:  # ESC键退出
                going = False
            else:
                global last_key
                last_key = e.key  # 记录最后按下的键
            if e.key == pg.K_h:  # h键显示帮助
                draw_usage_in_history(history, usage)
            if e.key == pg.K_c:  # c键切换控制器事件状态
                current_state = pygame._sdl2.controller.get_eventstate()
                pygame._sdl2.controller.set_eventstate(not current_state)

        if e.type == pg.MOUSEBUTTONDOWN and e.button == 1:  # 鼠标左键点击
            pg.event.set_grab(not pg.event.get_grab())  # 切换输入抓取状态

        if e.type == pg.MOUSEBUTTONDOWN and e.button == 3:  # 鼠标右键点击
            pg.mouse.set_visible(not pg.mouse.get_visible())  # 切换鼠标可见性

        if e.type != pg.MOUSEMOTION:  # 排除鼠标移动事件（太频繁）
            txt = f"{pg.event.event_name(e.type)}: {e.dict}"  # 格式化事件信息
            img = font.render(txt, 1, (50, 200, 50), (0, 0, 0))  # 渲染事件文本
            history.append(img)  # 添加到历史记录
            history = history[-13:]  # 保持最近13条记录

        if e.type == pg.VIDEORESIZE:  # 窗口大小调整事件
            win = pg.display.set_mode(e.size, pg.RESIZABLE)  # 重新设置窗口大小

        if e.type == pg.QUIT:  # 窗口关闭事件
            going = False
```