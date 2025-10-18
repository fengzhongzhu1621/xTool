# init()
```python
pygame.font.init()
```

# Font()

```python
self.font = pg.font.Font(None, 20)  # 创建字体
font = pg.font.Font(None, 30)  # 创建30号字体
font1 = pg.font.Font(None, 24)  # 创建24号字体
```

# SysFont()
```python
font = pg.font.SysFont("Arial", 24)  # 创建Arial字体，24号大小
```

# 设置字体
## set_italic()

```python
self.font.set_italic(1)  # 设置斜体
```

# 将文本消息渲染成图像
```python
self.total: int = 0
self.color: str = "white"  # 分数颜色
msg = f"分数: {self.total}"  # 创建分数文本
self.image: Surface = self.font.render(msg, 0, self.color)

text = font.render("Pummel The Chimp, And Win $$$", True, (10, 10, 10))  # 渲染文本
textpos = text.get_rect(centerx=background.get_width() / 2, y=10)  # 计算文本位置
background.blit(text, textpos)  # 将文本绘制到背景上
```

参数说明：
* msg: 要显示的文本内容（如"分数: 10"）
* 0: 抗锯齿参数（0表示不抗锯齿，1表示抗锯齿）
* self.color: 文本颜色（如"white"）

# 设置显示位置
```python
# 创建初始提示文本
spr_file_text = font.render("Drag and drop a file or image!!", 1, (255, 255, 255))  # 白色文本
spr_file_text_rect = spr_file_text.get_rect()  # 获取文本矩形区域
spr_file_text_rect.center = surf.get_rect().center  # 文本居中显示
```