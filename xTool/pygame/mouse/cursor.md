# 光标手势
system_cursor1 = pg.SYSTEM_CURSOR_CROSSHAIR
system_cursor2 = pg.SYSTEM_CURSOR_HAND
system_cursor3 = pg.SYSTEM_CURSOR_IBEAM


# 自定义光标
```python
# 创建系统光标 - 使用Pygame内置的系统光标类型
system_cursor1 = pg.SYSTEM_CURSOR_CROSSHAIR  # 十字准星光标
system_cursor2 = pg.SYSTEM_CURSOR_HAND  # 手型光标
system_cursor3 = pg.SYSTEM_CURSOR_IBEAM  # 文本输入光标（I型光标）


# 创建颜色光标 - 使用Surface对象创建自定义颜色光标
surf = pg.Surface((40, 40))
surf.fill((120, 50, 50))  # 填充深红色
color_cursor = pg.cursors.Cursor((20, 20), surf)  # 创建光标，热点在中心


# 创建图像光标 - 从图像文件加载光标
main_dir = os.path.split(os.path.abspath(__file__))[0]  # 获取当前文件所在目录
image_name = os.path.join(main_dir, "data", "cursor.png")  # 图像文件路径
image = pg.image.load(image_name)  # 加载图像
image_cursor = pg.cursors.Cursor((image.get_width() // 2, image.get_height() // 2), image)  # 创建图像光标，热点在中心


# 创建位图光标 - 使用字符串数组定义光标形状
# 尺寸为24x24像素
thickarrow_strings = (
    "XX                      ",  # 箭头形状的字符串表示
    "XXX                     ",  # 'X'表示黑色像素
    "XXXX                    ",  # '.'表示白色像素
    "XX.XX                   ",  # ' '表示透明像素
    "XX..XX                  ",
    "XX...XX                 ",
    "XX....XX                ",
    "XX.....XX               ",
    "XX......XX              ",
    "XX.......XX             ",
    "XX........XX            ",
    "XX........XXX           ",
    "XX......XXXXX           ",
    "XX.XXX..XX              ",
    "XXXX XX..XX             ",
    "XX   XX..XX             ",
    "     XX..XX             ",
    "      XX..XX            ",
    "      XX..XX            ",
    "       XXXX             ",
    "       XX               ",
    "                        ",
    "                        ",
    "                        ",
)

# 编译字符串为位图光标
bitmap_cursor1 = pg.cursors.Cursor(
    (24, 24),  # 光标尺寸
    (0, 0),  # 热点位置（左上角）
    *pg.cursors.compile(thickarrow_strings, black="X", white=".", xor="o"),  # 编译字符串数组
)


# 创建预定义的位图光标 - 使用Pygame内置的位图光标
bitmap_cursor2 = pg.cursors.diamond  # 菱形光标
```


# set_cursor()
```python
# 光标列表 - 包含所有可用的光标类型
cursors = [
    system_cursor1,  # 系统十字光标
    color_cursor,  # 颜色光标
    system_cursor2,  # 系统手型光标
    image_cursor,  # 图像光标
    system_cursor3,  # 系统文本光标
    bitmap_cursor1,  # 位图箭头光标
    bitmap_cursor2,  # 位图菱形光标
]
index = 0  # 当前光标索引
pg.mouse.set_cursor(cursors[index])  # 设置初始光标
```

# get_cursor()
```python
# 更新光标类型显示文本
bg.fill((183, 201, 226), (0, 15, bg.get_width(), 50))  # 清除文本区域
text1 = font.render((f"This is a {pg.mouse.get_cursor().type} cursor"), True, (0, 0, 0))
text_rect1 = text1.get_rect(center=(bg.get_width() / 2, 40))  # 文本居中
bg.blit(text1, text_rect1)  # 绘制文本
```