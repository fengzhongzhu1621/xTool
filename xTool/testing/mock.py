from xTool.misc import StringIO


class MockFile(StringIO):
    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class MockFS:
    def __init__(self):
        self.files = {}

    def open(self, name, mode="r", **kwargs):
        if name not in self.files:
            if "r" in mode:
                # If we are reading from a file, it should already exist
                raise FileNotFoundError(name)
            f = self.files[name] = MockFile()
        else:
            f = self.files[name]
            f.seek(0)
        return f

    def exists(self, name):
        return name in self.files
