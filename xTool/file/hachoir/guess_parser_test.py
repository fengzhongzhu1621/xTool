from pathlib import Path

from hachoir.parser import guessParser
from hachoir.stream import FileInputStream


def test_analyze_file_format():
    file_path = Path(__file__).parent.parent.parent.parent
    filename = file_path / "python.png"

    try:
        stream = FileInputStream(str(filename))
        parser = guessParser(stream)

        if not parser:
            return "未知格式"
        print(parser.PARSER_TAGS)
        # {
        #   'id': 'png',
        #   'category': 'image',
        #   'file_ext': ('png',),
        #   'mime': ('image/png', 'image/x-png'),
        #   'min_size': 64,
        #   'magic': [(b'\x89PNG\r\n\x1a\n', 0)],
        #   'description': 'Portable Network Graphics (PNG) picture',
        #   }
        info = {
            "格式": parser.PARSER_TAGS.get('file_ext', ['未知'])[0],
            "描述": parser.PARSER_TAGS.get('description', [''])[0],
            "魔数": parser.MAGIC.hex() if hasattr(parser, 'MAGIC') else None,
            "字段数": sum(1 for _ in parser),
        }

        print("\n".join(f"{k}: {v}" for k, v in info.items()))
        # 格式: png
        # 描述: P
        # 魔数: None
        # 字段数: 7
    except Exception as e:
        print(f"解析错误: {e}")
