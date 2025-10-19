# time

## Clock()
```python
# 创建游戏时钟对象，用于控制帧率
clock = pygame.time.Clock()
```

# wait()
```python
pygame.time.wait(1000)  # 等待1秒
```

# delay()
```python
pygame.time.delay(40)  # 短暂延迟防止连续点击
```

# set_timer()
```python
# 确保事件循环至少每0.5秒运行一次
pg.time.set_timer(pg.USEREVENT, 500)
```

