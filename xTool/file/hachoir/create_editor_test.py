from hachoir.editor import createEditor
from hachoir.parser import createParser


def test_modify_binary_comment():
    filename = "test.bin"
    parser = createParser(filename)
    editor = createEditor(parser)

    # 修改特定字段
    if "comment" in editor:
        editor["comment"].value = "Modified by Hachoir"

    # 保存修改
    with open("modified_" + filename, "wb") as f:
        editor.writeInto(f)
