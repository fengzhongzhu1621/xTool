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
# 设置定时器事件，每500毫秒触发一次USEREVENT
pg.time.set_timer(pg.USEREVENT, 500)
```

# get_ticks()
返回的是从 Pygame 初始化开始的毫秒数（整数），更适合游戏开发。
调用 get_ticks() 的开销非常低，适合在游戏循环中频繁使用。

功能说明
* 作用：返回从 Pygame 初始化（即调用 pygame.init() ）到当前时刻所经过的毫秒数。
* 返回值：一个整数，表示毫秒数（1秒 = 1000毫秒）。

典型用途：
* 计算时间间隔（例如游戏帧率控制、动画计时、倒计时等）。
* 记录事件发生的时间点（如玩家操作、敌人生成等）。

计算耗时
```python
import pygame

# 初始化 Pygame
pygame.init()

# 记录程序启动后的初始时间
start_time = pygame.time.get_ticks()

# 模拟一段耗时操作（例如加载资源或游戏循环）
pygame.time.delay(2000)  # 延迟 2000 毫秒（2秒）

# 获取当前时间
current_time = pygame.time.get_ticks()

# 计算时间差
elapsed_time = current_time - start_time
print(f"程序运行了 {elapsed_time} 毫秒")  # 输出：程序运行了 2000 毫秒
```

帧率控制
```python
clock = pygame.time.Clock()
while True:
    current_time = pygame.time.get_ticks()
    # 每 100 毫秒执行一次操作
    if current_time % 100 == 0:
        print("定时操作")
    clock.tick(60)  # 限制帧率为 60 FPS
```

倒计时
```python
start_time = pygame.time.get_ticks()
timeout = 5000  # 5 秒超时

while True:
    current_time = pygame.time.get_ticks()
    if current_time - start_time >= timeout:
        print("时间到！")
        break
```

动画计时
```python
animation_start = pygame.time.get_ticks()
animation_duration = 3000  # 动画持续 3 秒

while True:
    elapsed = pygame.time.get_ticks() - animation_start
    if elapsed < animation_duration:
        progress = elapsed / animation_duration  # 计算动画进度（0.0 到 1.0）
        print(f"动画进度: {progress:.2f}")
    else:
        print("动画结束")
        break
```
