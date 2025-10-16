# 加载图片

返回一个包含球体图像数据的Surface对象。这个Surface对象会保留图像文件中的颜色键信息以及alpha透明度设置

```python
# 加载球体图片并获取其矩形区域
ball = pygame.image.load("intro_ball.gif")

# Pygame提供了一个名为Rect的实用工具对象类型，它用于表示一个矩形区域。
ballrect = ball.get_rect()
```

# 移动矩形

```python
ballrect = ballrect.move(speed)
```