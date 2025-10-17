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
```

```python
SCREENRECT = pg.Rect(0, 0, 640, 480)  # 屏幕矩形区域
winstyle = 0  # 窗口模式
bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)  # 获取最佳颜色深度
screen = pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)  # 创建显示窗口
```

# flip()

Pygame通过双缓冲机制来管理屏幕显示。

当我们完成绘图操作后，会调用 `pygame.display.flip()将完整的显示内容更新到屏幕上` 这个方法。这样一来，我们在屏幕上绘制的所有内容才会真正显示出来。这种双缓冲机制确保了用户看到的只有那些已经完全绘制完成的画面；如果没有这种机制，用户就会看到那些还在绘制过程中的、尚未完成的画面部分。

```python
# 刷新显示，将你的工作呈现在屏幕上
pygame.display.flip()
```

# set_icon() 设置窗口图标
```python
pg.display.set_icon(icon)
```

# set_caption() 设置窗口标题
```python
pg.display.set_caption("Pygame Aliens")
```
