# 加载图片

返回一个包含球体图像数据的Surface对象。这个Surface对象会保留图像文件中的颜色键信息以及alpha透明度设置

```python
# 加载球体图片并获取其矩形区域
ball = pygame.image.load("intro_ball.gif")

# Pygame提供了一个名为Rect的实用工具对象类型，它用于表示一个矩形区域。
# 返回一个 Rect 对象，表示图像的矩形边界， 默认位置是 (0, 0)，在屏幕左上角，但可以通过参数设置特定位置
ballrect = ball.get_rect()

# 将玩家放置在屏幕底部中央
# 屏幕区域 (SCREENRECT):
# ┌─────────────────┐
# │                 │
# │                 │
# │                 │
# │                 │
# │       🚀        │  ← 玩家出现在这里 (midbottom对齐)
# └─────────────────┘
# midbottom 是矩形底边的中点坐标，将玩家矩形的底边中点对齐到屏幕底边中点
self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
```

Rect 的其他常用对齐点：

topleft, topright, bottomleft, bottomright
midtop, midleft, midright, center
