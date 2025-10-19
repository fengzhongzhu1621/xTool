# PixelArray()
```python
# 演示1: 创建渐变效果
# 创建PixelArray对象
ar = pg.PixelArray(surface)

# 创建简单的灰度渐变效果
# 从黑色(0,0,0)渐变到白色(255,255,255)
for y in range(255):
    r, g, b = y, y, y  # RGB值相同，创建灰度
    ar[:, y] = (r, g, b)  # 设置整列像素的颜色
del ar  # 删除PixelArray对象以解锁表面
show(surface)  # 显示渐变效果
```
