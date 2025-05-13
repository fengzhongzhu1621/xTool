from pathlib import Path

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser


def test_analyze_image():
    file_path = Path(__file__).parent.parent.parent.parent
    filename = file_path / "python.png"
    parser = createParser(str(filename))
    if not parser:
        print(f"无法解析文件: {filename}")
        return

    metadata = extractMetadata(parser)
    if metadata:
        print(metadata)  # PngMetadata
        # Metadata:
        # - Image width: 705 pixels
        # - Image height: 300 pixels
        # - Bits/pixel: 32
        # - Pixel format: RGBA
        # - Compression rate: 32.2x
        # - Image DPI width: 7558 DPI
        # - Image DPI height: 7558 DPI
        # - Compression: deflate
        # - MIME type: image/png
        # - Endianness: Big endian
        print(f"图片尺寸: {metadata.get('width')}x{metadata.get('height')}")
        print(f"格式: {metadata.get('mime_type')}")
