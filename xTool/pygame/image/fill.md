# fill()

```python
# 混合模式切换
elif event.key == pg.K_a:
    blendtype = pg.BLEND_ADD  # 加法混合
    changed = True
elif event.key == pg.K_s:
    blendtype = pg.BLEND_SUB  # 减法混合
    changed = True
elif event.key == pg.K_m:
    blendtype = pg.BLEND_MULT  # 乘法混合
    changed = True
elif event.key == pg.K_PLUS:
    blendtype = pg.BLEND_MAX  # 最大值混合
    changed = True
elif event.key == pg.K_MINUS:
    blendtype = pg.BLEND_MIN  # 最小值混合
    changed = True

# 应用颜色混合效果（对整个图像应用混合）
# 功能：使用指定颜色和混合模式填充整个混合图像
# 参数：
#   - color: 当前选择的颜色值 [R, G, B]
#   - None: 表示对整个图像区域进行填充
#   - blendtype: 混合模式（如ADD、SUB、MULT等）
# 作用：将颜色与图像像素按照指定混合模式进行合成
blendimage.fill(color, None, blendtype)
```