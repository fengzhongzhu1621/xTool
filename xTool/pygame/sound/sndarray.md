# array()
```python
# 将声音转换为numpy数组
a1 = pg.sndarray.array(sound)
if mydebug:
    print(f"原始声音数组形状: {a1.shape}")
    print(f"SHAPE1: {a1.shape}")

length = a1.shape[0]  # 原始声音的采样点数量

# 创建用于存储回声的数组
# myarr = zeros(length+12000)  # 旧方法
myarr = zeros(a1.shape, int32)  # 创建与原始声音相同形状的数组

 # 回声持续时间（秒）
echo_length = 3.5
# 根据声音的维度（单声道/立体声）计算新数组的大小
if len(a1.shape) > 1:
    # 立体声：两个声道
    # mult = a1.shape[1]  # 声道数量
    size = (a1.shape[0] + int(echo_length * a1.shape[0]), a1.shape[1])
    # size = (a1.shape[0] + int(a1.shape[0] + (echo_length * 3000)), a1.shape[1])
else:
    # 单声道
    # mult = 1
    size = (a1.shape[0] + int(echo_length * a1.shape[0]),)
    # size = (a1.shape[0] + int(a1.shape[0] + (echo_length * 3000)),)

```

# make_sound()
```python
# 将数组转换回声音对象（转换为16位有符号整数）
sound2 = pg.sndarray.make_sound(myarr.astype(int16))
```
