# circle()

```python
(function) def circle(
    surface: Surface,
    color: ColorValue,
    center: Coordinate,
    radius: float, # 半径
    width: int = 0,
    draw_top_right: bool = False,
    draw_top_left: bool = False,
    draw_bottom_left: bool = False,
    draw_bottom_right: bool = False
) -> Rect
```

```python
# 在屏幕上绘制红色圆形，半径为40像素
pygame.draw.circle(screen, "red", player_pos, 40)
# 在屏幕上绘制一个绿色实心圆形
pygame.draw.circle(screen, "green", (50, 100), 10)
# 在绿色圆形上绘制黑色边框（仅绘制边框，不填充）
pygame.draw.circle(screen, "black", (50, 100), 10, 1)
```    
