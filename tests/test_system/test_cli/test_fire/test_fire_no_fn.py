"""
在任何Python程序结束时调用fire.Fire()。 这会将程序的全部内容暴露给命令行
"""

import fire


def add(x, y):
    return x + y


def multiply(x, y):
    return x * y


if __name__ == '__main__':
    fire.Fire()
