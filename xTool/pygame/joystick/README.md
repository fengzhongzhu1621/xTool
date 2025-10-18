# get_count()
```python
pg.joystick.get_count()


# 如果没有连接任何设备
if not pg.joystick.get_count():
    img = font.render("No Joysticks to Initialize", 1, (50, 200, 50), (0, 0, 0))
    history.append(img)  # 添加提示信息
```

# Joystick()
```python
import pygame._sdl2.controller

# 初始化游戏手柄/控制器
for x in range(pg.joystick.get_count()):  # 遍历所有连接的设备
    if pygame._sdl2.controller.is_controller(x):  # 检查是否为控制器
        c = pygame._sdl2.controller.Controller(x)  # 创建控制器对象
        txt = "Enabled controller: " + c.name  # 控制器名称
    else:  # 普通游戏手柄
        j = pg.joystick.Joystick(x)  # 创建游戏手柄对象
        txt = "Enabled joystick: " + j.get_name()  # 手柄名称

    img = font.render(txt, 1, (50, 200, 50), (0, 0, 0))  # 渲染设备信息
    history.append(img)  # 添加到历史记录
```

