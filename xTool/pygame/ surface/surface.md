# Surface()

```python
s = pygame.Surface(screen.get_size(), pygame.SRCALPHA, 32)

# 创建基础表面im1（红色背景）
im1 = pg.Surface(screen.get_size())
# im1= im1.convert()  # 可选的颜色格式转换
im1.fill((100, 0, 0))  # 填充红色(RGB:100,0,0)

# 创建第二个表面im2（绿色背景）
im2 = pg.Surface(screen.get_size())
im2.fill((0, 50, 0))  # 填充绿色(RGB:0,50,0)
# 创建带透明度的副本
# im3= im2.convert(SRCALPHA)  # 可选：创建带alpha通道的副本
im3 = im2
im3.set_alpha(127)  # 设置透明度为127（半透明）

# 创建用于捕获图像的表面。为了性能考虑，位深度应与显示表面相同
self.display = pg.display.set_mode(self.size)
self.snapshot = pg.surface.Surface(self.size, 0, self.display)

# 创建背景
background = pg.Surface(screen.get_size())  # 创建与屏幕相同尺寸的表面
background = background.convert()  # 转换为显示格式
background.fill((170, 238, 187))  # 填充浅绿色背景

# # 填充浅蓝色背景
_ = bg.fill((183, 201, 226))
```

参数解释：

* screen.get_size() - 获取屏幕的尺寸，使Surface与屏幕大小相同
* pygame.SRCALPHA - 标志位，表示Surface支持每像素透明度（alpha通道）
* 32 - 颜色深度，32位表示RGBA（红绿蓝透明度各8位）

功能说明：

* 创建了一个与屏幕大小相同的透明画布
* 支持抗锯齿绘制，因为透明背景可以平滑混合边缘
* 常用于需要叠加效果或平滑边缘的图形绘制

