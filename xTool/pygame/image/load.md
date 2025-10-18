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

img_to_blit = im2.convert()  # 转换为标准格式
iaa = img_to_blit.convert_alpha()  # 转换为带alpha通道的格式
```

Rect 的其他常用对齐点：

topleft, topright, bottomleft, bottomright
midtop, midleft, midright, center

# 设置图片的位置
```python
# 尝试打开文件，如果是图像文件则加载显示
filetype = ev.file[-3:]  # 获取文件扩展名（后3个字符）
if filetype in ["png", "bmp", "jpg"]:  # 检查是否为支持的图像格式
    spr_file_image = pg.image.load(ev.file).convert()  # 加载并转换图像
    spr_file_image.set_alpha(127)  # 设置半透明效果（alpha值127）
    spr_file_image_rect = spr_file_image.get_rect()  # 获取图像矩形区域
    spr_file_image_rect.center = surf.get_rect().center  # 图像居中显示
```