import resource


def test_getrlimit():
    # RLIMIT_AS 表示进程的虚拟内存（地址空间）限制，即进程可以使用的最大内存（包括物理内存和交换空间）
    # 获取当前进程的最大内存限制
    # soft：软限制（当前生效的限制）。
    # hard：硬限制（管理员设置的最大限制，普通用户不能超过它）。
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    print(f"当前进程的最大内存限制为: {soft / (1024 * 1024)} MB")
