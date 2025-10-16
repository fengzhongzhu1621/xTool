import mistune


def convert_markdown_to_html_file(md_file_path: str, html_file_path: str) -> str:
    """将存在的md文件解析并保存为html文件"""
    parser = mistune.Markdown(hard_wrap=True)
    with open(md_file_path, encoding="utf-8") as read_file, open(html_file_path, "w", encoding="utf-8") as write_file:
        # 读取md文件内容
        md_version_log = read_file.read()
        # 解析md文件内容
        html_version_log = parser(md_version_log)
        # 保存html文件
        write_file.write(html_version_log)
    return html_version_log
