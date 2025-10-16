"""
brew install libmagic

python-magic 是 libmagic 的封装，是一个文件类型识别库。
"""

import os

try:
    import magic
except ImportError:
    magic = None


def test_ascii_text():
    m = magic.Magic()

    file = __file__
    file_type = m.from_file(file)
    assert file_type == "Python script, Unicode text, UTF-8 text executable"


def test_image_type():
    m = magic.Magic(mime=True)
    file_type = m.from_file(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "python.png"))
    assert file_type == "image/png"
