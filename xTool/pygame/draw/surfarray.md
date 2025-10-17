# surfarray.blit_array()

参数说明：

* screen - 目标 Surface（屏幕表面）
* array_img - 包含像素数据的 NumPy 数组

具体功能：

* 数据转换：将 NumPy 数组中的数值数据转换为 Pygame 可以显示的像素格式
* 像素映射：将数组中的每个元素对应到屏幕上的每个像素
* 高效绘制：比传统的逐像素绘制方法快得多，因为利用了 NumPy 的向量化操作

工作流程：

* 数组的维度决定了绘制的区域大小
* 数组的值决定了每个像素的颜色
* 对于 RGB 图像，数组形状通常是 (高度, 宽度, 3)，每个像素有 R、G、B 三个通道值

```python
array_img = np.zeros((128, 128), int32)
screen = pg.display.set_mode(array_img.shape[:2], 0, 32)
surfarray.blit_array(screen, array_img)

# 创建一个 100x100 的红色图像数组
red_array = np.full((100, 100, 3), [255, 0, 0], dtype=np.uint8)
# 将数组绘制到屏幕上
surfarray.blit_array(screen, red_array)
```

# surfarray.array3d()

```python
rgbarray = surfarray.array3d(imgsurface)
# 功能：将Surface对象转换为3D NumPy数组
# - surfarray.array3d() 是Pygame的数组转换函数
# - 将图像数据转换为形状为 (高度, 宽度, 3) 的3D数组
# - 每个像素对应一个RGB三元组 [R, G, B]
# - 数组元素类型通常为uint8（0-255范围）
# - 这种转换允许使用NumPy进行高效的图像处理操作
```