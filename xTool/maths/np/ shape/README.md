shape 是 NumPy 数组的一个属性（不是函数），它返回数组的维度信息。在 Pygame 的 surfarray 模块中，图像数据通常被表示为 NumPy 数组。

```python
screen = pg.display.set_mode(array_img.shape[:2], 0, 32)
```

* 对于图像数组，通常是 (高度, 宽度, 通道数) 或 (高度, 宽度)
* 例如：(480, 640, 3) 表示 480像素高 × 640像素宽 × 3个颜色通道（RGB）

[:2] - 切片操作，取前两个元素

* 从 (高度, 宽度, 通道数) 中提取 (高度, 宽度)
* 例如：(480, 640, 3)[:2] → (480, 640)

```python
# 假设 array_img 是一个 480×640×3 的 RGB 图像数组
array_img.shape        # 返回 (480, 640, 3)
array_img.shape[:2]    # 返回 (480, 640)
# pg.display.set_mode((480, 640), 0, 32) 创建 480×640 的窗口
```
