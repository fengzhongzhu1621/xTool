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

# get_size() 获得屏幕大小
```python
screen.get_size() - 获取屏幕的尺寸，使Surface与屏幕大小相同

# 初始化玩家位置为屏幕中心
player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
```

# blit() 绘制图片Rect

所谓“blit”操作，本质上就是将一个图像中的像素颜色复制到另一个图像中。在调用blit方法时，我们需要指定一个源图像 Surface，以及目标图像中该图像应该被放置的位置。

```python
# 将球体绘制到屏幕上
screen.blit(ball, ballrect)

# 将绘制好的Surface复制到屏幕上
screen.blit(s, (0, 0))

# 从源图像中提取20x20像素的方块并绘制到屏幕上
# 参数说明：源图像，目标位置(x,y)，源图像区域(xpos,ypos,20,20)
screen.blit(bitmap, (x, y), (xpos, ypos, 20, 20))
```

# set_palette()
```python
# 确保图像和屏幕使用相同的格式
if screen.get_bitsize() == 8:
    # 如果是8位色深，设置屏幕调色板与图像一致
    screen.set_palette(bitmap.get_palette())
```
