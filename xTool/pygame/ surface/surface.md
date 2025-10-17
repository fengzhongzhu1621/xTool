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
```

参数解释：

* screen.get_size() - 获取屏幕的尺寸，使Surface与屏幕大小相同
* pygame.SRCALPHA - 标志位，表示Surface支持每像素透明度（alpha通道）
* 32 - 颜色深度，32位表示RGBA（红绿蓝透明度各8位）

功能说明：

* 创建了一个与屏幕大小相同的透明画布
* 支持抗锯齿绘制，因为透明背景可以平滑混合边缘
* 常用于需要叠加效果或平滑边缘的图形绘制

