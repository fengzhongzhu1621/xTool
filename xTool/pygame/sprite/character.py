from .sprite import Sprite


class Character(Sprite):
    """
    用于显示关卡信息的字符基类，所有字符显示组件的父类
    """

    def __init__(self, image, *groups):
        """
        初始化字符精灵

        Args:
            image: 字符图像表面(Surface)对象
        """
        super().__init__(*groups)  # 调用父类Sprite的初始化方法
        self.image = image  # 存储字符图像
        self.rect = self.image.get_rect()  # 获取图像矩形区域用于定位和碰撞检测
