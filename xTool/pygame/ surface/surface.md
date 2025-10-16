# Surface()

```python
s = pygame.Surface(screen.get_size(), pygame.SRCALPHA, 32)
```

参数解释：

* screen.get_size() - 获取屏幕的尺寸，使Surface与屏幕大小相同
* pygame.SRCALPHA - 标志位，表示Surface支持每像素透明度（alpha通道）
* 32 - 颜色深度，32位表示RGBA（红绿蓝透明度各8位）

功能说明：

* 创建了一个与屏幕大小相同的透明画布
* 支持抗锯齿绘制，因为透明背景可以平滑混合边缘
* 常用于需要叠加效果或平滑边缘的图形绘制

