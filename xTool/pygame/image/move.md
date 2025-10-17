# move()

```python
ballrect = ballrect.move(speed)
```

# move_ip()
```python
# 根据方向移动玩家
self.rect.move_ip(direction * self.speed, 0)
```

move_ip() 方法:

* ip 表示 "in-place"（原地操作）
* 直接修改当前 Rect 对象的位置
* 不返回新的 Rect 对象

参数说明:

* direction * self.speed: 水平移动距离
  * direction: 方向（1=向右，-1=向左）
  * self.speed: 移动速度
* 0: 垂直移动距离（0表示不垂直移动）


与 move() 函数的对比：

| 特性     | move_ip()    | move()         |
| -------- | ------------ | -------------- |
| 操作方式 | 原地修改     | 返回新对象     |
| 返回值   | 无（None）   | 新的 Rect 对象 |
| 内存使用 | 更高效       | 创建新对象     |
| 使用场景 | 直接更新位置 | 需要保留原位置 |


```python
# 使用 move_ip() - 原地修改
rect = pygame.Rect(0, 0, 50, 50)
rect.move_ip(10, 5)  # rect 现在在 (10, 5)

# 使用 move() - 返回新对象
rect = pygame.Rect(0, 0, 50, 50)
new_rect = rect.move(10, 5)  # rect 仍在 (0, 0), new_rect 在 (10, 5)
```

# clamp()

```python
# 确保玩家不会移出屏幕，限制玩家矩形在屏幕边界内
self.rect = self.rect.clamp(SCREENRECT)
```
方法功能：

* 将当前矩形限制在另一个矩形（SCREENRECT）的边界内
* 如果当前矩形超出边界，会被移动到最近的合法位置
* 返回一个新的 Rect 对象

实际效果：

* 防止玩家移动到屏幕外
* 确保玩家始终可见在游戏区域内

边界处理规则：

* 如果矩形宽度 ≤ 边界宽度：确保整个矩形在边界内
* 如果矩形宽度 > 边界宽度：将矩形居中于边界

