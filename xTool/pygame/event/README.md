# 事件类型 event type
```python
pygame.QUIT
pygame.KEYDOWN
```

# event key
```
pygame.K_ESCAPE
```

# event.unicode
event.unicode

# get()
```python
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
```


# wait()
```python
# 事件循环，等待用户操作
try:
    while True:
        # 等待事件
        event = pygame.event.wait()
        if event.type == pygame.QUIT:  # 点击关闭按钮
            break
        if event.type == pygame.KEYDOWN:  # 按键事件
            if event.key == pygame.K_ESCAPE or event.unicode == "q":  # ESC或Q键退出
                break
        pygame.display.flip()  # 刷新显示
finally:
    pygame.quit()  # 退出pygame
```
