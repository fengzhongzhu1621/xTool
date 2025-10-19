# info()
```python
# 创建一个使用屏幕80%大小的窗口
info = pg.display.Info()  # 获取显示信息
w = info.current_w  # 屏幕宽度
h = info.current_h  # 屏幕高度
```

# get_surface()
```python
screen = pg.display.get_surface()
self.area = screen.get_rect()
```

# set_mode()
设置显示模式

pg.SCALED

* 启用硬件加速的缩放功能
* 允许窗口大小自动适应屏幕分辨率
* 提供更平滑的缩放效果
* 当窗口大小与屏幕分辨率不匹配时，自动进行缩放
* 保持宽高比，避免图像变形
* 使用 GPU 加速，性能更好
* 在全屏模式下自动适应不同分辨率
* 在窗口模式下提供更好的缩放体验
* 特别是对于高分辨率显示器的兼容性

```python
# 创建游戏窗口，设置分辨率为1280x720
screen: pygame.Surface = pygame.display.set_mode((1280, 720))

SCREEN_SIZE = pg.Vector2(1000, 600)  # 屏幕尺寸
screen = pg.display.set_mode(SCREEN_SIZE)  # 创建屏幕

# 创建硬件加速的双缓冲显示表面
screen = pg.display.set_mode((640, 480), pg.HWSURFACE | pg.DOUBLEBUF)
```

```python
SCREENRECT = pg.Rect(0, 0, 640, 480)  # 屏幕矩形区域
winstyle = 0  # 窗口模式
bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)  # 获取最佳颜色深度
screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)  # 创建显示窗口
```

根据屏幕大小创建窗口

```python
# 创建一个使用屏幕80%大小的窗口
info = pg.display.Info()  # 获取显示信息
w = info.current_w  # 屏幕宽度
h = info.current_h  # 屏幕高度
pg.display.set_mode((int(w * 0.8), int(h * 0.8)))  # 设置窗口大小
```

# flip()

Pygame通过双缓冲机制来管理屏幕显示。

当我们完成绘图操作后，会调用 `pygame.display.flip()将完整的显示内容更新到屏幕上` 这个方法。这样一来，我们在屏幕上绘制的所有内容才会真正显示出来。这种双缓冲机制确保了用户看到的只有那些已经完全绘制完成的画面；如果没有这种机制，用户就会看到那些还在绘制过程中的、尚未完成的画面部分。

```python
# 刷新显示，将你的工作呈现在屏幕上
pygame.display.flip()
```

# update()
display.flip()
* 更新整个屏幕：强制重绘整个显示表面
* 性能较低：每次调用都会更新所有像素
* 适用于：需要完全重绘整个屏幕的场景
* 使用场景：游戏主循环中，当所有内容都需要更新时

display.update()
* 智能更新：可以只更新指定区域或发生变化的区域
* 性能较高：只更新需要变化的部分
* 参数灵活：
    * update()：更新整个屏幕（与flip相同）
    * update(rect)：更新指定矩形区域
    * update(rect_list)：更新多个矩形区域
* 适用于：部分内容更新的场景，提高性能

```python
# 初始化时更新整个屏幕
pg.display.update()  # 等同于 pg.display.flip()

# 在循环中只更新按钮区域
pg.display.update()  # 这里应该使用区域更新来优化性能

# 只在按钮点击时更新按钮区域
if button_clicked:
    pg.display.update(button_rect)  # 只更新按钮区域
else:
    pg.display.update()  # 或者使用无参数更新整个屏幕
```

# set_icon() 设置窗口图标
```python
pg.display.set_icon(icon)
```

# set_caption() 设置窗口标题
```python
pg.display.set_caption("Pygame Aliens")
```

# 调整窗口大小事件
if e.type == pg.VIDEORESIZE:  # 窗口大小调整事件
    win = pg.display.set_mode(e.size, pg.RESIZABLE)  # 重新设置窗口大小

