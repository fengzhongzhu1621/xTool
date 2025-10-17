"""pygame.examples.camera
Pygame 相机示例

使用pygame.camera进行基本的图像捕获和显示

键盘控制说明
-----------------

- 0键：启动相机0
- 1键：启动相机1
- 9键：启动相机9
- 10键：启动相机...等等！没有10键！
"""

import pygame as pg
import pygame.camera


class VideoCapturePlayer:
    """视频捕获播放器类"""

    size = (640, 480)  # 默认图像尺寸

    def __init__(self, **argd):
        """初始化视频捕获播放器"""
        self.__dict__.update(**argd)
        super().__init__(**argd)

        # 创建显示表面，标准的pygame操作
        self.display = pg.display.set_mode(self.size)
        self.init_cams(0)  # 初始化默认相机

    def init_cams(self, which_cam_idx):
        """初始化指定索引的相机

        参数:
            which_cam_idx: 相机索引

        返回:
            使用的相机ID
        """
        # 获取可用相机列表
        self.clist = pygame.camera.list_cameras()

        # 确保至少有一个相机存在
        if not self.clist:
            raise ValueError("抱歉，未检测到相机。")

        # 检查指定的相机索引是否存在，如果不存在则使用列表中的第一个相机
        try:
            cam_id = self.clist[which_cam_idx]
        except IndexError:
            cam_id = self.clist[0]

        # 创建指定尺寸和RGB色彩空间的相机对象
        self.camera = pygame.camera.Camera(cam_id, self.size, "RGB")

        # 启动相机
        self.camera.start()

        self.clock = pg.time.Clock()  # 创建时钟对象用于控制帧率

        # 创建用于捕获图像的表面。为了性能考虑，位深度应与显示表面相同
        self.snapshot = pg.surface.Surface(self.size, 0, self.display)
        # 返回正在使用的相机名称，用于包含在窗口标题中
        return cam_id

    def get_and_flip(self):
        """获取相机图像并更新显示

        注意：如果不想将帧率与相机绑定，可以检查相机是否有图像就绪。
        虽然这在大多数相机上有效，但有些相机可能永远不会返回true。
        """
        # 直接从相机获取图像到显示表面（优化性能）
        self.snapshot = self.camera.get_image(self.display)

        # 以下是备选的图像获取方式（注释掉的代码）：
        # if 0 and self.camera.query_image():
        #     # 捕获图像
        #     self.snapshot = self.camera.get_image(self.snapshot)

        # if 0:
        #     self.snapshot = self.camera.get_image(self.snapshot)
        #     # self.snapshot = self.camera.get_image()

        #     # 将图像绘制到显示表面，很简单！
        #     self.display.blit(self.snapshot, (0, 0))
        # else:
        #     self.snapshot = self.camera.get_image(self.display)
        #     # self.display.blit(self.snapshot, (0,0))

        pg.display.flip()  # 更新显示

    def main(self):
        """主循环：处理用户输入和相机切换"""
        # 获取相机列表。如果没有相机，抛出错误
        clist = pygame.camera.list_cameras()
        if not clist:
            raise ValueError("抱歉，未检测到相机。")
        # 获取第一个相机作为默认相机。我们希望显示包含相机名称
        camera = clist[0]

        # 为用户创建易于理解的选项列表
        print("\n按下对应的数字键来选择要显示的相机！")
        print("（选择不存在的相机会默认使用相机0）")
        for index, cam in enumerate(clist):
            print(f"[{index}]: {cam}")

        going = True
        while going:
            events = pg.event.get()
            for e in events:
                # 退出条件：窗口关闭或ESC键
                if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
                    going = False
                # 处理数字键（0-9）切换相机
                if e.type == pg.KEYDOWN:
                    if e.key in range(pg.K_0, pg.K_0 + 10):
                        camera = self.init_cams(e.key - pg.K_0)  # 初始化指定索引的相机

            # 获取图像并更新显示
            self.get_and_flip()

            # 控制帧率
            self.clock.tick()

            # 设置窗口标题：显示相机名称和当前帧率
            pygame.display.set_caption(f"{camera} ({self.clock.get_fps():.2f} FPS)")


def main():
    """主函数：初始化Pygame和相机，启动视频捕获播放器"""
    pg.init()  # 初始化Pygame

    pygame.camera.init()  # 初始化相机模块
    VideoCapturePlayer().main()  # 创建视频捕获播放器并启动主循环

    pg.quit()  # 退出Pygame


if __name__ == "__main__":
    main()
