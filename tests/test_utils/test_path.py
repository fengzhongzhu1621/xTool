from xTool.file_io.path import path_to_dotted


def test_path_to_dotted():
    actual = path_to_dotted("/usr/local/", "/")
    expect = "usr.local"
    assert actual == expect
