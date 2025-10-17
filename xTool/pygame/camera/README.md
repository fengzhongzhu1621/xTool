# init()
```python
pygame.camera.init()
```

# list_cameras()
```python
# 获取可用相机列表
self.clist = pygame.camera.list_cameras()
```

# Camera()
```python
# 检查指定的相机索引是否存在，如果不存在则使用列表中的第一个相机
try:
    cam_id = self.clist[which_cam_idx]
except IndexError:
    cam_id = self.clist[0]
    
# 创建指定尺寸和RGB色彩空间的相机对象
self.camera = pygame.camera.Camera(cam_id, self.size, "RGB")
# 启动相机
self.camera.start()

# 直接从相机获取图像到显示表面（优化性能）
self.snapshot = self.camera.get_image(self.display)
```
