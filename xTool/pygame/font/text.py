from pygame import Surface
from pygame.font import Font


def showtext(win: Surface, font: Font, pos, text, color, bgcolor):
    """在指定位置显示文本

    参数:
        win: 目标窗口表面
        pos: 文本位置 (x, y)
        text: 要显示的文本
        color: 文本颜色
        bgcolor: 背景颜色

    返回:
        下一个文本的起始位置
    """
    textimg = font.render(text, 1, color, bgcolor)  # 渲染文本
    win.blit(textimg, pos)  # 绘制文本到窗口
    return pos[0] + textimg.get_width() + 5, pos[1]  # 返回下一个文本位置
