import numpy as np


def test_np_zeros():
    # 创建一个长度为5的一维浮点数数组
    arr_1d = np.zeros(5)
    print(arr_1d)  # [0. 0. 0. 0. 0.]

    # 创建一个3行2列的二维数组。​​注意​​：形状必须用元组 (3, 2)表示
    arr_2d = np.zeros((3, 2))
    print(arr_2d)
    # 输出:
    # [[0. 0.]
    #  [0. 0.]
    #  [0. 0.]]

    # 创建三维数组
    arr_3d = np.zeros((2, 3, 4))
    print(arr_3d)
    # [[[0. 0. 0. 0.]
    #   [0. 0. 0. 0.]
    #   [0. 0. 0. 0.]]

    #  [[0. 0. 0. 0.]
    #   [0. 0. 0. 0.]
    #   [0. 0. 0. 0.]]]

    # 指定数据类型
    arr_int = np.zeros((2, 2), dtype=int)
    print(arr_int)
    # 输出:
    # [[0 0]
    #  [0 0]]
