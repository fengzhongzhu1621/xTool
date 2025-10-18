# rect()
```python
# 初始化按钮 - 用于切换光标
button_text = font1.render("Click here to change cursor", True, (0, 0, 0))  # 渲染按钮文本
button = pg.draw.rect(
    bg,
    (180, 180, 180),
    (139, 300, button_text.get_width() + 5, button_text.get_height() + 50),
)

# 绘制按钮文本
button_text_rect = button_text.get_rect(center=button.center)  # 文本居中
_ = bg.blit(button_text, button_text_rect)
```

