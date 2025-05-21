# 简介
Pythran通过预先编译,将python代码转为C++代码的 后缀为 .so 的文件,从而 在运行时获得更快的运行速度;

# 适用场景
* 大数据量矩阵运算
* 信号处理、图像处理算法
* 科学模拟、物理建模
* 任何需要“Python 写，C++ 跑”的高性能场景

# 安装
1.pip（Debian/Ubuntu）
```shell
sudo apt-get install libatlas-base-dev python-dev python-ply python-numpy
pip install pythran
```

2.conda-forge（跨平台）
```shell
mamba install -c conda-forge pythran
或者
conda install -c conda-forge pythran
```

3.MacOS＋Homebrew
```shell
pip install pythran
brew install openblas
printf '[compiler]\nblas=openblas\ninclude_dirs=/usr/local/opt/openblas/include\nlibrary_dirs=/usr/local/opt/openblas/lib'>~/.pythranrc
```

# 执行
```shell
pythran dprod.py

>>> import dprod
>>> dprod.dprod([1, 2], [3, 4])
11
```
# 配置
~/.pythranrc

# export
注解接口：使用 ```#pythran export``` 精确声明输入输出类型，帮助 Pythran 做静态分析。

## 函数入参设置
```shell
argument_type = basic_type
              | (argument_type+)    # this is a tuple 元祖
              | argument_type list    # this is a list 列表
              | argument_type set    # this is a set 集合
              | argument_type []+    # this is a ndarray, C-style 是个ndarray
              | argument_type [::]+    # this is a strided ndarray
              | argument_type [:,...,:]+ # this is a ndarray, Cython style
              | argument_type [:,...,3]+ # this is a ndarray, some dimension fixed
              | argument_type:argument_type dict    # this is a dictionary 是个字典

basic_type = bool | byte | int | float | str | None | slice
           | uint8 | uint16 | uint32 | uint64 | uintp
           | int8 | int16 | int32 | int64 | intp
           | float32 | float64 | float128
           | complex64 | complex128 | complex256
```
