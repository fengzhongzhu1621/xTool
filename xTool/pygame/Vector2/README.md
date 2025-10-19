# Vector2()

pygame.Vector2 是 Pygame 库中的一个二维向量类，用于表示和操作二维空间中的点、方向、速度等向量数据。

```python
# 初始化玩家位置为屏幕中心
player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
```

# move_towards_ip()
```python
# 控制帧率为60FPS，并获取时间增量
delta_time = clock.tick(60)
# 使用move_towards_ip方法让球体向目标位置移动
# 移动距离 = 速度 × 时间增量
o.position.move_towards_ip(target_position, o.speed * delta_time)
```
