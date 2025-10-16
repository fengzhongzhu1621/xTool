# 按键值
```python
pygame.K_w # W键：向上移动
pygame.K_s # S键：向下移动
pygame.K_a # A键：向左移动
pygame.K_d # D键：向右移动
pygame.K_ESCAPE
```

# get_pressed()
```python
# 获取键盘按键状态
keys = pygame.key.get_pressed()
# 根据WASD键控制圆形移动（y 轴向下）
if keys[pygame.K_w]:  # W键：向上移动
    player_pos.y -= 300 * dt
if keys[pygame.K_s]:  # S键：向下移动
    player_pos.y += 300 * dt
if keys[pygame.K_a]:  # A键：向左移动
    player_pos.x -= 300 * dt
if keys[pygame.K_d]:  # D键：向右移动
    player_pos.x += 300 * dt
```

