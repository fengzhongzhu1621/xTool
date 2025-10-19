
# 特点

* 基于FreeType2字体引擎
* 提供更高级的字体渲染功能
* 支持更多字体格式和高级特性

# 高级特性：

* 旋转文本：支持任意角度旋转
* 混合效果：支持Alpha混合
* 样式组合：粗体、斜体、下划线等样式组合
* 垂直文本：支持垂直方向渲染
* 精确控制：更精细的字体度量控制
* 更多格式：支持更多字体文件格式

# 字体类型
freetype.STYLE_UNDERLINE
freetype.STYLE_OBLIQUE


# freetype()

```python
import pygame.freetype as freetype
font = freetype.Font(os.path.join(fontdir, "data", "sans.ttf"))  # 加载字体文件

# 设置下划线调整和填充
font.underline_adjustment = 0.5  # 下划线位置调整
font.pad = True  # 启用填充


# 垂直文本演示（保持英文文本不变）
font.vertical = True  # 启用垂直文本
font.render_to(screen, (32, 200), "Vertical?", "blue3", None, size=32)
font.vertical = False  # 禁用垂直文本

```

# render_to()
```python
# 渲染带下划线和斜体的"Hello World"（保持英文文本不变）
font.render_to(
    screen,
    (32, 32),
    "Hello World",
    "red3",
    "dimgray",
    size=64,
    style=freetype.STYLE_UNDERLINE | freetype.STYLE_OBLIQUE,
)
font.pad = False  # 禁用填充

# 渲染字母序列（保持英文文本不变）
font.render_to(
    screen,
    (32, 128),
    "abcdefghijklm",
    "dimgray",
    "green3",
    size=64,
)
```
