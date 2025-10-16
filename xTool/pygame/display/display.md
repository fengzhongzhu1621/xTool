# display

## set_mode()
```python
# 创建游戏窗口，设置分辨率为1280x720
screen: pygame.Surface = pygame.display.set_mode((1280, 720))
```

## flip()

Pygame通过双缓冲机制来管理屏幕显示。

当我们完成绘图操作后，会调用 `pygame.display.flip()将完整的显示内容更新到屏幕上` 这个方法。这样一来，我们在屏幕上绘制的所有内容才会真正显示出来。这种双缓冲机制确保了用户看到的只有那些已经完全绘制完成的画面；如果没有这种机制，用户就会看到那些还在绘制过程中的、尚未完成的画面部分。

```python
# 刷新显示，将你的工作呈现在屏幕上
pygame.display.flip()
```

