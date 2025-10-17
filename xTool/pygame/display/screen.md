# fill()
```python
# 用颜色填充屏幕，清除上一帧的内容
_ = screen.fill("purple")

# 用黑色填充屏幕，擦除屏幕上的内容
screen.fill(black)

# 用红色填充屏幕背景
screen.fill((255, 0, 0))

screen.fill((100, 100, 100))
```

# 获得屏幕大小
```python
screen.get_size() - 获取屏幕的尺寸，使Surface与屏幕大小相同

# 初始化玩家位置为屏幕中心
player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
```


# 绘制图片Rect

所谓“blit”操作，本质上就是将一个图像中的像素颜色复制到另一个图像中。在调用blit方法时，我们需要指定一个源图像 Surface，以及目标图像中该图像应该被放置的位置。

```python
# 将球体绘制到屏幕上
screen.blit(ball, ballrect)

# 将绘制好的Surface复制到屏幕上
screen.blit(s, (0, 0))
```