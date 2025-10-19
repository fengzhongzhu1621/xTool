# from_surface()

```python
# 加载图像和生成遮罩
images = []
masks = []
for image_path in args:
    # 加载图像并转换为带透明通道的格式
    images.append(pg.image.load(image_path).convert_alpha())
    # 从图像表面生成遮罩
    masks.append(pg.mask.from_surface(images[-1]))
```
