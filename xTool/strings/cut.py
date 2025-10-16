def cut_content(content: str, max_len_per_line: int = 1024) -> list[str]:
    """
    智能分割长文本内容，生成不超过指定长度的段落

    参数:
        content: 需要分割的原始文本内容
        max_len_per_line: 每个段落的最大字符数（默认1024）

    返回:
        list[str]: 分割后的文本段落列表，满足：
        1. 每段长度 <= max_len_per_line
        2. 优先在换行处分割
        3. 处理超长单行文本
    """
    if max_len_per_line <= 0:
        raise ValueError("最大长度需大于0")

    paragraphs = []
    current_para = ""

    # 按换行符预分割文本
    lines = content.split('\n')

    for line_num, line in enumerate(lines):
        # 处理空行保留换行结构
        if not line:
            if len(current_para) + 1 <= max_len_per_line:
                current_para += '\n'
            else:
                paragraphs.append(current_para.rstrip('\n'))
                current_para = '\n'
            continue

        # 处理超长单行文本
        while len(line) > max_len_per_line:
            split_pos = max_len_per_line - len(current_para)
            if split_pos > 0:
                current_para += line[:split_pos]
                line = line[split_pos:]
            paragraphs.append(current_para.rstrip('\n'))
            current_para = ""

            # 寻找合适的分割点（避免切断词语）
            while split_pos < len(line):
                if line[split_pos] in ('。', '！', '？', '；', ',', ' ', '\t'):
                    break
                split_pos += 1
            split_pos = min(split_pos, max_len_per_line)

            paragraphs.append(line[:split_pos])
            line = line[split_pos:]

        # 正常添加逻辑
        new_content = f"{current_para}{line}\n"
        if len(new_content) > max_len_per_line:
            paragraphs.append(current_para.rstrip('\n'))
            current_para = f"{line}\n"
        else:
            current_para = new_content

        # 最后一行处理
        if line_num == len(lines) - 1 and current_para:
            paragraphs.append(current_para.rstrip('\n'))

    return paragraphs
