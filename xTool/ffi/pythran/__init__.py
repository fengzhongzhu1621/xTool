import sys

if sys.platform != "win32":
    import distutils.msvccompiler

    def get_build_version():
        return 0  # 返回一个默认值

    distutils.msvccompiler.get_build_version = get_build_version
