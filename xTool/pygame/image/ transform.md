# 缩放图像
```python
icon = pygame.transform.scale(surface, size)

# 加载输入图像
i = pygame.image.load(fin)

# 检查是否支持平滑缩放（smoothscale），如果支持则使用平滑缩放
if hasattr(pygame.transform, "smoothscale"):
    scaled_image = pygame.transform.smoothscale(i, (w, h))
else:
    # 如果不支持平滑缩放，使用普通缩放
    scaled_image = pygame.transform.scale(i, (w, h))


# 加载图像并进行四倍放大
imagename = os.path.join(main_dir, "data", "liquid.bmp")
bitmap = pg.image.load(imagename)
bitmap = pg.transform.scale2x(bitmap)  # 第一次2倍放大
bitmap = pg.transform.scale2x(bitmap)  # 第二次2倍放大（总共4倍）
# 确保图像和屏幕使用相同的格式
if screen.get_bitsize() == 8:
    # 如果是8位色深，设置屏幕调色板与图像一致
    screen.set_palette(bitmap.get_palette())
else:
    # 否则将图像转换为屏幕格式
    bitmap = bitmap.convert()
```

参数说明：

* surface: 要缩放的原始图像表面（Surface对象）
* size: 目标尺寸，是一个包含两个整数的元组 (width, height)


功能作用：
* 图像缩放: 将输入的 surface 图像缩放到指定的 size 尺寸
* 创建新表面: 返回一个新的 Surface 对象，包含缩放后的图像
* 图标优化: 通常用于将较大的图像缩放到适合作为窗口图标的小尺寸（如 32x32 像素）


# 翻转图像
```python
img = image.load_image(os.path.join(resource_dir, "player1.gif"))
Player.images = [img, pg.transform.flip(img, 1, 0)]  # 玩家左右图像
```

flip() 函数用于翻转图像
* 参数 1 表示水平翻转（x轴方向）
* 参数 0 表示不垂直翻转（y轴方向）
* 效果：将原始图像水平镜像，创建面向左侧的图像

结果数组:

* [img, pg.transform.flip(img, 1, 0)]
* 第一个元素：原始图像（面向右侧）
* 第二个元素：翻转后的图像（面向左侧）


实际效果：
* 当玩家向右移动时，使用第一个图像
* 当玩家向左移动时，使用第二个图像（镜像版本）
* 这样就不需要为左右方向分别制作两张图像
