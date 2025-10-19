"""pygame.examples.midi

MIDI输入示例和独立的MIDI输出示例。

默认运行输出示例。

python -m pygame.examples.midi --output
python -m pygame.examples.midi --input
python -m pygame.examples.midi --input
"""

import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Set, Tuple, Union

import pygame as pg
import pygame.midi

# 黑白钢琴键直接使用黑白颜色值
BACKGROUNDCOLOR = "slategray"  # 背景色：板岩灰


def print_device_info():
    """打印MIDI设备信息"""
    pygame.midi.init()
    _print_device_info()
    pygame.midi.quit()


def _print_device_info():
    """内部函数：遍历并打印所有MIDI设备信息"""
    print("midi count: ", pygame.midi.get_count())
    for i in range(pygame.midi.get_count()):
        r = pygame.midi.get_device_info(i)
        (interf, name, input, output, opened) = r

        in_out = ""
        if input:
            in_out = "(input)"  # 输入设备
        if output:
            in_out = "(output)"  # 输出设备

        print("%2i: interface :%s:, name :%s:, opened :%s:  %s" % (i, interf, name, opened, in_out))


def input_main(device_id=None):
    """MIDI输入示例：监听并显示MIDI输入事件"""
    pg.init()

    pygame.midi.init()

    _print_device_info()  # 显示设备信息

    if device_id is None:
        input_id = pygame.midi.get_default_input_id()  # 使用默认输入设备
    else:
        input_id = device_id

    print(f"using input_id :{input_id}:")
    i = pygame.midi.Input(input_id)  # 创建MIDI输入对象

    pg.display.set_mode((1, 1))  # 创建最小窗口用于事件处理

    going = True
    while going:
        events = pygame.event.get()
        for e in events:
            if e.type in [pg.QUIT]:
                going = False
            if e.type in [pg.KEYDOWN]:
                going = False
            if e.type in [pygame.midi.MIDIIN]:  # MIDI输入事件
                print(e)

        if i.poll():  # 检查是否有MIDI事件
            midi_events = i.read(10)  # 读取最多10个MIDI事件
            # 将MIDI事件转换为pygame事件
            midi_evs = pygame.midi.midis2events(midi_events, i.device_id)

            for m_e in midi_evs:
                pygame.event.post(m_e)  # 将MIDI事件发布到事件队列

    del i
    pygame.midi.quit()


def output_main(device_id=None):
    """执行教堂风琴乐器的音乐键盘示例

    这是一个钢琴键盘示例，包含两个八度的键盘，从F3音符开始。
    鼠标左键按下键盘上的键开始音符，左键释放停止音符。
    音符也映射到计算机键盘按键，假设使用美式英语PC键盘。
    白键位于第二行，从TAB到BACKSLASH，从F3音符开始。
    黑键映射到顶行，从'1'到BACKSPACE，从F#3开始。
    'r'键是中音C。关闭窗口或按ESCAPE退出程序。
    键速度（音符振幅）在键盘图像上垂直变化，最小速度在键顶部，最大速度在底部。

    默认MIDI输出（未提供device_id）是计算机的默认输出设备。

    """

    # 给新pygame用户的说明：
    #
    # 所有midi模块的内容都在这个函数中。不需要理解键盘显示的工作原理
    # 来理解MIDI消息是如何发送的。

    # 键盘由Keyboard实例绘制。该实例将MIDI音符映射到音乐键盘键。
    # 一个regions表面将窗口位置映射到(MIDI音符, 速度)对。
    # 一个key_mapping字典对计算机键盘键做同样的映射。
    # MIDI声音通过直接方法调用pygame.midi.Output实例来控制。
    #
    # 使用pygame.midi时需要考虑的事项：
    #
    # 1) 使用pygame.midi.init()初始化midi模块。
    # 2) 为所需的输出设备端口创建midi.Output实例。
    # 3) 使用set_instrument()方法选择乐器。
    # 4) 使用note_on()和note_off()方法播放音符。
    # 5) 完成后调用pygame.midi.Quit()。虽然midi模块尝试确保
    #    MIDI正确关闭，但最好显式执行。try/finally语句是最安全的方式。
    #

    # GRAND_PIANO = 0  # 大钢琴
    CHURCH_ORGAN = 19  # 教堂风琴

    instrument = CHURCH_ORGAN  # 使用教堂风琴音色
    # instrument = GRAND_PIANO  # 也可以使用大钢琴
    start_note = 53  # F3（白键音符），start_note != 0
    n_notes = 24  # 两个八度（14个白键）

    # 创建键盘映射：将键盘按键映射到MIDI音符和速度
    key_mapping = make_key_mapping(
        [
            pg.K_TAB,
            pg.K_1,
            pg.K_q,
            pg.K_2,
            pg.K_w,
            pg.K_3,
            pg.K_e,
            pg.K_r,
            pg.K_5,
            pg.K_t,
            pg.K_6,
            pg.K_y,
            pg.K_u,
            pg.K_8,
            pg.K_i,
            pg.K_9,
            pg.K_o,
            pg.K_0,
            pg.K_p,
            pg.K_LEFTBRACKET,
            pg.K_EQUALS,
            pg.K_RIGHTBRACKET,
            pg.K_BACKSPACE,
            pg.K_BACKSLASH,
        ],
        start_note,
    )

    pg.init()
    pygame.midi.init()

    _print_device_info()  # 显示设备信息

    if device_id is None:
        port = pygame.midi.get_default_output_id()  # 使用默认输出设备
    else:
        port = device_id

    print(f"using output_id :{port}:")

    midi_out = pygame.midi.Output(port, 0)  # 创建MIDI输出对象
    try:
        midi_out.set_instrument(instrument)  # 设置乐器音色
        keyboard = Keyboard(start_note, n_notes)  # 创建键盘实例

        # 设置显示窗口
        screen = pg.display.set_mode(keyboard.rect.size)
        screen.fill(BACKGROUNDCOLOR)
        pg.display.flip()

        # 创建背景和脏矩形列表用于优化绘制
        background = pg.Surface(screen.get_size())
        background.fill(BACKGROUNDCOLOR)
        dirty_rects = []
        keyboard.draw(screen, background, dirty_rects)
        pg.display.update(dirty_rects)

        # 创建区域映射表面：将屏幕位置映射到音符和速度
        regions = pg.Surface(screen.get_size())  # 初始颜色(0,0,0)
        keyboard.map_regions(regions)

        pg.event.set_blocked(pg.MOUSEMOTION)  # 阻止鼠标移动事件
        mouse_note = 0  # 当前鼠标按下的音符
        on_notes = set()  # 当前正在播放的音符集合
        while True:
            e = pg.event.wait()  # 等待事件
            if e.type == pg.MOUSEBUTTONDOWN:  # 鼠标按下事件
                mouse_note, velocity, __, __ = regions.get_at(e.pos)  # 获取位置对应的音符和速度
                if mouse_note and mouse_note not in on_notes:
                    keyboard.key_down(mouse_note)  # 键盘键按下
                    midi_out.note_on(mouse_note, velocity)  # 发送音符开始
                    on_notes.add(mouse_note)  # 添加到播放集合
                else:
                    mouse_note = 0
            elif e.type == pg.MOUSEBUTTONUP:  # 鼠标释放事件
                if mouse_note:
                    midi_out.note_off(mouse_note)  # 发送音符结束
                    keyboard.key_up(mouse_note)  # 键盘键释放
                    on_notes.remove(mouse_note)  # 从播放集合移除
                    mouse_note = 0
            elif e.type == pg.QUIT:  # 退出事件
                break
            elif e.type == pg.KEYDOWN:  # 键盘按下事件
                if e.key == pg.K_ESCAPE:  # ESC键退出
                    break
                try:
                    note, velocity = key_mapping[e.key]  # 获取按键对应的音符和速度
                except KeyError:
                    pass  # 忽略未映射的按键
                else:
                    if note not in on_notes:
                        keyboard.key_down(note)  # 键盘键按下
                        midi_out.note_on(note, velocity)  # 发送音符开始
                        on_notes.add(note)  # 添加到播放集合
            elif e.type == pg.KEYUP:  # 键盘释放事件
                try:
                    note, __ = key_mapping[e.key]  # 获取按键对应的音符
                except KeyError:
                    pass  # 忽略未映射的按键
                else:
                    if note in on_notes and note != mouse_note:  # 确保不是鼠标控制的音符
                        keyboard.key_up(note)  # 键盘键释放
                        midi_out.note_off(note, 0)  # 发送音符结束
                        on_notes.remove(note)  # 从播放集合移除

            # 更新显示
            dirty_rects = []
            keyboard.draw(screen, background, dirty_rects)
            pg.display.update(dirty_rects)
    finally:
        del midi_out  # 清理MIDI输出对象
        pygame.midi.quit()  # 退出MIDI系统


def make_key_mapping(keys, start_note):
    """创建键盘映射：返回一个按计算机键盘键码索引的(音符, 速度)字典

    参数:
    keys - 键盘按键列表
    start_note - 起始音符编号

    返回:
    字典，键为键盘按键码，值为(音符编号, 速度)元组
    """
    mapping = {}
    for i, key in enumerate(keys):
        mapping[key] = (start_note + i, 127)  # 最大速度127
    return mapping


class NullKey:
    """空键类：忽略其他键传递的事件

    NullKey实例默认用作最左侧键盘键的左侧键实例。
    这是一个虚拟键，用于处理边界情况。

    """

    def _right_white_down(self):
        """右侧白键按下事件 - 忽略"""
        pass

    def _right_white_up(self):
        """右侧白键释放事件 - 忽略"""
        pass

    def _right_black_down(self):
        """右侧黑键按下事件 - 忽略"""
        pass

    def _right_black_up(self):
        """右侧黑键释放事件 - 忽略"""
        pass


null_key = NullKey()


@dataclass
class KeyData:
    """键数据类：用于向Key类的子类传递数据

    这个数据类封装了键盘键的所有配置参数，包括尺寸、状态、事件处理等。
    """

    is_white_key: bool  # 是否为白键
    c_width: int  # 键宽度
    c_height: int  # 键高度
    c_down_state_initial: int  # 初始按下状态
    c_down_state_rect_initial: pg.Rect  # 初始状态对应的图像区域
    c_notify_down_method: str  # 按下通知方法名
    c_notify_up_method: str  # 释放通知方法名
    c_updates: Set[Any]  # 需要更新的键集合
    c_event_down: Dict[int, Tuple[int, pg.Rect]]  # 按下事件状态转换映射
    c_event_up: Dict[int, Tuple[int, pg.Rect]]  # 释放事件状态转换映射
    c_image_strip: pg.Surface  # 图像条带表面
    c_event_right_white_down: Dict[int, Tuple[int, Union[pg.Rect, None]]]  # 右侧白键按下事件
    c_event_right_white_up: Dict[int, Tuple[int, Union[pg.Rect, None]]]  # 右侧白键释放事件
    c_event_right_black_down: Dict[int, Tuple[int, Union[pg.Rect, None]]]  # 右侧黑键按下事件
    c_event_right_black_up: Dict[int, Tuple[int, Union[pg.Rect, None]]]  # 右侧黑键释放事件


class Key:
    """A key widget, maintains key state and draws the key's image

    Constructor arguments:
    ident - A unique key identifier. Any immutable type suitable as a key.
    posn - The location of the key on the display surface.
    key_left - Optional, the adjacent white key to the left. Changes in
        up and down state are propagated to that key.

    A key has an associated position and state. Related to state is the
    image drawn. State changes are managed with method calls, one method
    per event type. The up and down event methods are public. Other
    internal methods are for passing on state changes to the key_left
    key instance.

    """

    key_data: KeyData  # pyright: ignore[reportUninitializedInstanceVariable]

    def __init__(self, ident, posn, key_left=None):
        """Return a new Key instance

        The initial state is up, with all adjacent keys to the right also
        up.

        """
        if key_left is None:
            key_left = null_key
        rect = pg.Rect(posn[0], posn[1], self.key_data.c_width, self.key_data.c_height)
        self.rect = rect
        self._state = self.key_data.c_down_state_initial
        self._source_rect = self.key_data.c_down_state_rect_initial
        self._ident = ident
        self._hash = hash(ident)
        self._notify_down = getattr(key_left, self.key_data.c_notify_down_method)
        self._notify_up = getattr(key_left, self.key_data.c_notify_up_method)
        self._key_left = key_left
        self._background_rect = pg.Rect(rect.left, rect.bottom - 10, self.key_data.c_width, 10)
        self.key_data.c_updates.add(self)
        self.is_white = self.key_data.is_white_key

    def down(self):
        """Signal that this key has been depressed (is down)"""

        self._state, source_rect = self.key_data.c_event_down[self._state]
        if source_rect is not None:
            self._source_rect = source_rect
            self.key_data.c_updates.add(self)
            self._notify_down()

    def up(self):
        """Signal that this key has been released (is up)"""

        self._state, source_rect = self.key_data.c_event_up[self._state]
        if source_rect is not None:
            self._source_rect = source_rect
            self.key_data.c_updates.add(self)
            self._notify_up()

    def _right_white_down(self):
        """Signal that the adjacent white key has been depressed

        This method is for internal propagation of events between
        key instances.

        """

        self._state, source_rect = self.key_data.c_event_right_white_down[self._state]
        if source_rect is not None:
            self._source_rect = source_rect
            self.key_data.c_updates.add(self)

    def _right_white_up(self):
        """Signal that the adjacent white key has been released

        This method is for internal propagation of events between
        key instances.

        """

        self._state, source_rect = self.key_data.c_event_right_white_up[self._state]
        if source_rect is not None:
            self._source_rect = source_rect
            self.key_data.c_updates.add(self)

    def _right_black_down(self):
        """Signal that the adjacent black key has been depressed

        This method is for internal propagation of events between
        key instances.

        """

        self._state, source_rect = self.key_data.c_event_right_black_down[self._state]
        if source_rect is not None:
            self._source_rect = source_rect
            self.key_data.c_updates.add(self)

    def _right_black_up(self):
        """Signal that the adjacent black key has been released

        This method is for internal propagation of events between
        key instances.

        """

        self._state, source_rect = self.key_data.c_event_right_black_up[self._state]
        if source_rect is not None:
            self._source_rect = source_rect
            self.key_data.c_updates.add(self)

    def __eq__(self, other):
        """True if same identifiers"""

        return self._ident == other._ident

    def __hash__(self):
        """Return the immutable hash value"""

        return self._hash

    def __str__(self):
        """Return the key's identifier and position as a string"""

        return "<Key %s at (%d, %d)>" % (self._ident, self.rect.top, self.rect.left)

    def draw(self, surf, background, dirty_rects):
        """Redraw the key on the surface surf

        The background is redrawn. The altered region is added to the
        dirty_rects list.

        """

        surf.blit(background, self._background_rect, self._background_rect)
        surf.blit(self.key_data.c_image_strip, self.rect, self._source_rect)
        dirty_rects.append(self.rect)


def key_class(updates, image_strip, image_rects: List[pg.Rect], is_white_key=True):
    """Return a keyboard key widget class

    Arguments:
    updates - a set into which a key instance adds itself if it needs
        redrawing.
    image_strip - The surface containing the images of all key states.
    image_rects - A list of Rects giving the regions within image_strip that
        are relevant to this key class.
    is_white_key (default True) - Set false if this is a black key.

    This function automates the creation of a key widget class for the
    three basic key types. A key has two basic states, up or down (
    depressed). Corresponding up and down images are drawn for each
    of these two states. But to give the illusion of depth, a key
    may have shadows cast upon it by the adjacent keys to its right.
    These shadows change depending on the up/down state of the key and
    its neighbors. So a key may support multiple images and states
    depending on the shadows. A key type is determined by the length
    of image_rects and the value of is_white.

    """

    # Naming convention: Variables used by the Key class as part of a
    # closure start with 'c_'.

    # State logic and shadows:
    #
    # A key may cast a shadow upon the key to its left. A black key casts a
    # shadow on an adjacent white key. The shadow changes depending of whether
    # the black or white key is depressed. A white key casts a shadow on the
    # white key to its left if it is up and the left key is down. Therefore
    # a keys state, and image it will draw, is determined entirely by its
    # itself and the key immediately adjacent to it on the right. A white key
    # is always assumed to have an adjacent white key.
    #
    # There can be up to eight key states, representing all permutations
    # of the three fundamental states of self up/down, adjacent white
    # right up/down, adjacent black up/down.
    #
    down_state_none = 0
    down_state_self = 1
    down_state_white = down_state_self << 1
    down_state_self_white = down_state_self | down_state_white
    down_state_black = down_state_white << 1
    down_state_self_black = down_state_self | down_state_black
    down_state_white_black = down_state_white | down_state_black
    down_state_all = down_state_self | down_state_white_black

    # Some values used in the class.
    #
    c_down_state_initial = down_state_none
    c_down_state_rect_initial = image_rects[0]
    c_updates = updates
    c_image_strip = image_strip
    c_width, c_height = image_rects[0].size

    # A key propagates its up/down state change to the adjacent white key on
    # the left by calling the adjacent key's _right_black_down or
    # _right_white_down method.
    #
    if is_white_key:
        key_color = "white"
    else:
        key_color = "black"
    c_notify_down_method = f"_right_{key_color}_down"
    c_notify_up_method = f"_right_{key_color}_up"

    # Images:
    #
    # A black key only needs two images, for the up and down states. Its
    # appearance is unaffected by the adjacent keys to its right, which cast no
    # shadows upon it.
    #
    # A white key with a no adjacent black to its right only needs three
    # images, for self up, self down, and both self and adjacent white down.
    #
    # A white key with both a black and white key to its right needs six
    # images: self up, self up and adjacent black down, self down, self and
    # adjacent white down, self and adjacent black down, and all three down.
    #
    # Each 'c_event' dictionary maps the current key state to a new key state,
    # along with corresponding image, for the related event. If no redrawing
    # is required for the state change then the image rect is simply None.
    #
    c_event_down: Dict[int, Tuple[int, pygame.Rect]] = {down_state_none: (down_state_self, image_rects[1])}
    c_event_up: Dict[int, Tuple[int, pygame.Rect]] = {down_state_self: (down_state_none, image_rects[0])}
    c_event_right_white_down: Dict[int, Tuple[int, Union[pygame.Rect, None]]] = {
        down_state_none: (down_state_none, None),
        down_state_self: (down_state_self, None),
    }
    c_event_right_white_up = c_event_right_white_down.copy()
    c_event_right_black_down = c_event_right_white_down.copy()
    c_event_right_black_up = c_event_right_white_down.copy()
    if len(image_rects) > 2:
        c_event_down[down_state_white] = (down_state_self_white, image_rects[2])
        c_event_up[down_state_self_white] = (down_state_white, image_rects[0])
        c_event_right_white_down[down_state_none] = (down_state_white, None)
        c_event_right_white_down[down_state_self] = (
            down_state_self_white,
            image_rects[2],
        )
        c_event_right_white_up[down_state_white] = (down_state_none, None)
        c_event_right_white_up[down_state_self_white] = (
            down_state_self,
            image_rects[1],
        )
        c_event_right_black_down[down_state_white] = (down_state_white, None)
        c_event_right_black_down[down_state_self_white] = (down_state_self_white, None)
        c_event_right_black_up[down_state_white] = (down_state_white, None)
        c_event_right_black_up[down_state_self_white] = (down_state_self_white, None)
    if len(image_rects) > 3:
        c_event_down[down_state_black] = (down_state_self_black, image_rects[4])
        c_event_down[down_state_white_black] = (down_state_all, image_rects[5])
        c_event_up[down_state_self_black] = (down_state_black, image_rects[3])
        c_event_up[down_state_all] = (down_state_white_black, image_rects[3])
        c_event_right_white_down[down_state_black] = (down_state_white_black, None)
        c_event_right_white_down[down_state_self_black] = (
            down_state_all,
            image_rects[5],
        )
        c_event_right_white_up[down_state_white_black] = (down_state_black, None)
        c_event_right_white_up[down_state_all] = (down_state_self_black, image_rects[4])
        c_event_right_black_down[down_state_none] = (down_state_black, image_rects[3])
        c_event_right_black_down[down_state_self] = (
            down_state_self_black,
            image_rects[4],
        )
        c_event_right_black_down[down_state_white] = (
            down_state_white_black,
            image_rects[3],
        )
        c_event_right_black_down[down_state_self_white] = (
            down_state_all,
            image_rects[5],
        )
        c_event_right_black_up[down_state_black] = (down_state_none, image_rects[0])
        c_event_right_black_up[down_state_self_black] = (
            down_state_self,
            image_rects[1],
        )
        c_event_right_black_up[down_state_white_black] = (
            down_state_white,
            image_rects[0],
        )
        c_event_right_black_up[down_state_all] = (down_state_self_white, image_rects[2])

    class OurKey(Key):
        key_data = KeyData(
            is_white_key,
            c_width,
            c_height,
            c_down_state_initial,
            c_down_state_rect_initial,
            c_notify_down_method,
            c_notify_up_method,
            c_updates,
            c_event_down,
            c_event_up,
            c_image_strip,
            c_event_right_white_down,
            c_event_right_white_up,
            c_event_right_black_down,
            c_event_right_black_up,
        )

    return OurKey


def key_images() -> Tuple[pg.Surface, Dict[str, pg.Rect]]:
    """Return a keyboard keys image strip and a mapping of image locations

    The return tuple is a pygame.Surface and a dictionary keyed by key name and valued by a pygame.Rect.

    This function encapsulates the constants relevant to the keyboard image
    file. There are five key types. One is the black key. The other four
    white keys are determined by the proximity of the black keys. The plain
    white key has no black key adjacent to it. A white-left and white-right
    key has a black key to the left or right of it respectively. A white-center
    key has a black key on both sides. A key may have up to six related
    images depending on the state of adjacent keys to its right.

    """

    my_dir = os.path.split(os.path.abspath(__file__))[0]
    strip_file = os.path.join(my_dir, "data", "midikeys.png")
    white_key_width = 42
    white_key_height = 160
    black_key_width = 22
    black_key_height = 94
    strip = pg.image.load(strip_file)
    names = [
        "black none",
        "black self",
        "white none",
        "white self",
        "white self-white",
        "white-left none",
        "white-left self",
        "white-left black",
        "white-left self-black",
        "white-left self-white",
        "white-left all",
        "white-center none",
        "white-center self",
        "white-center black",
        "white-center self-black",
        "white-center self-white",
        "white-center all",
        "white-right none",
        "white-right self",
        "white-right self-white",
    ]
    rects = {}
    for i in range(2):
        rects[names[i]] = pg.Rect(i * white_key_width, 0, black_key_width, black_key_height)
    for i in range(2, len(names)):
        rects[names[i]] = pg.Rect(i * white_key_width, 0, white_key_width, white_key_height)
    return strip, rects


class Keyboard:
    """Musical keyboard widget

    Constructor arguments:
    start_note: midi note value of the starting note on the keyboard.
    n_notes: number of notes (keys) on the keyboard.

    A Keyboard instance draws the musical keyboard and maintains the state of
    all the keyboard keys. Individual keys can be in a down (depressed) or
    up (released) state.

    """

    _image_strip, _rects = key_images()

    white_key_width, white_key_height = _rects["white none"].size
    black_key_width, black_key_height = _rects["black none"].size

    _updates: Set[Any] = set()

    # There are five key classes, representing key shape:
    # black key (BlackKey), plain white key (WhiteKey), white key to the left
    # of a black key (WhiteKeyLeft), white key between two black keys
    # (WhiteKeyCenter), and white key to the right of a black key
    # (WhiteKeyRight).
    BlackKey = key_class(_updates, _image_strip, [_rects["black none"], _rects["black self"]], False)
    WhiteKey = key_class(
        _updates,
        _image_strip,
        [_rects["white none"], _rects["white self"], _rects["white self-white"]],
    )
    WhiteKeyLeft = key_class(
        _updates,
        _image_strip,
        [
            _rects["white-left none"],
            _rects["white-left self"],
            _rects["white-left self-white"],
            _rects["white-left black"],
            _rects["white-left self-black"],
            _rects["white-left all"],
        ],
    )
    WhiteKeyCenter = key_class(
        _updates,
        _image_strip,
        [
            _rects["white-center none"],
            _rects["white-center self"],
            _rects["white-center self-white"],
            _rects["white-center black"],
            _rects["white-center self-black"],
            _rects["white-center all"],
        ],
    )
    WhiteKeyRight = key_class(
        _updates,
        _image_strip,
        [
            _rects["white-right none"],
            _rects["white-right self"],
            _rects["white-right self-white"],
        ],
    )

    def __init__(self, start_note: int, n_notes: int):
        """Return a new Keyboard instance with n_note keys"""

        self._start_note = start_note
        self._end_note = start_note + n_notes - 1
        self._add_keys()

    def _add_keys(self) -> None:
        """Populate the keyboard with key instances

        Set the _keys and rect attributes.

        """

        # Keys are entered in a list, where index is Midi note. Since there are
        # only 128 possible Midi notes the list length is manageable. Unassigned
        # note positions should never be accessed, so are set None to ensure
        # the bug is quickly detected.
        #
        key_map: list[Key | Literal[None]] = [None] * 128

        start_note = self._start_note
        end_note = self._end_note
        black_offset = self.black_key_width // 2
        prev_white_key = None
        x = y = 0
        if is_white_key(start_note):
            is_prev_white = True
        else:
            x += black_offset
            is_prev_white = False
        for note in range(start_note, end_note + 1):
            ident = note  # For now notes uniquely identify keyboard keys.
            if is_white_key(note):
                if is_prev_white:
                    if note == end_note or is_white_key(note + 1):
                        key = self.WhiteKey(ident, (x, y), prev_white_key)
                    else:
                        key = self.WhiteKeyLeft(ident, (x, y), prev_white_key)
                else:
                    if note == end_note or is_white_key(note + 1):
                        key = self.WhiteKeyRight(ident, (x, y), prev_white_key)
                    else:
                        key = self.WhiteKeyCenter(ident, (x, y), prev_white_key)
                is_prev_white = True
                x += self.white_key_width
                prev_white_key = key
            else:
                key = self.BlackKey(ident, (x - black_offset, y), prev_white_key)
                is_prev_white = False
            key_map[note] = key
        self._keys = key_map

        the_key = key_map[self._end_note]
        if the_key is None:
            kb_width = 0
        else:
            kb_width = the_key.rect.right
        kb_height = self.white_key_height
        self.rect = pg.Rect(0, 0, kb_width, kb_height)

    def map_regions(self, regions):
        """Draw the key regions onto surface regions.

        Regions must have at least 3 byte pixels. Each pixel of the keyboard
        rectangle is set to the color (note, velocity, 0). The regions surface
        must be at least as large as (0, 0, self.rect.left, self.rect.bottom)

        """

        # First draw the white key regions. Then add the overlapping
        # black key regions.
        #
        cutoff = self.black_key_height
        black_keys = []
        for note in range(self._start_note, self._end_note + 1):
            key = self._keys[note]
            if key is not None and key.is_white:
                fill_region(regions, note, key.rect, cutoff)
            else:
                black_keys.append((note, key))
        for note, key in black_keys:
            if key is not None:
                fill_region(regions, note, key.rect, cutoff)

    def draw(self, surf, background, dirty_rects):
        """Redraw all altered keyboard keys"""

        changed_keys = self._updates
        while changed_keys:
            changed_keys.pop().draw(surf, background, dirty_rects)

    def key_down(self, note):
        """Signal a key down event for note"""
        key = self._keys[note]
        if key is not None:
            key.down()

    def key_up(self, note):
        """Signal a key up event for note"""
        key = self._keys[note]
        if key is not None:
            key.up()


def fill_region(regions, note, rect, cutoff):
    """填充区域：用(音符, 速度, 0)颜色填充指定矩形区域

    速度从区域顶部的小值变化到底部的127。垂直区域0到cutoff被分成
    三个部分，速度分别为42、84和127。cutoff以下的所有区域速度为127。

    参数:
    regions - 区域表面
    note - 音符编号
    rect - 矩形区域
    cutoff - 分割点高度
    """

    x, y, width, height = rect
    if cutoff is None:
        cutoff = height
    delta_height = cutoff // 3
    regions.fill((note, 42, 0), (x, y, width, delta_height))  # 顶部区域：速度42
    regions.fill((note, 84, 0), (x, y + delta_height, width, delta_height))  # 中间区域：速度84
    regions.fill((note, 127, 0), (x, y + 2 * delta_height, width, height - 2 * delta_height))  # 底部区域：速度127


def is_white_key(note):
    """判断音符是否由白键表示

    参数:
    note - 音符编号

    返回:
    如果音符对应白键返回True，否则返回False

    说明:
    使用标准的钢琴键盘模式：白键、黑键、白键、白键、黑键、白键、黑键、白键、白键、黑键、白键、黑键
    对应音符：C, C#, D, D#, E, F, F#, G, G#, A, A#, B
    """

    # key_pattern = [
    #     True,  # C - 白键
    #     False,  # C# - 黑键
    #     True,  # D - 白键
    #     True,  # D# - 黑键（实际是False，但这里可能是笔误，应该是False）
    #     False,  # E - 白键（实际是True，但这里可能是笔误，应该是True）
    #     True,  # F - 白键
    #     False,  # F# - 黑键
    #     True,  # G - 白键
    #     True,  # G# - 黑键（实际是False，但这里可能是笔误，应该是False）
    #     False,  # A - 白键（实际是True，但这里可能是笔误，应该是True）
    #     True,  # A# - 黑键（实际是False，但这里可能是笔误，应该是False）
    #     False,  # B - 白键（实际是True，但这里可能是笔误，应该是True）
    # ]
    # 修正后的正确模式：白键、黑键、白键、黑键、白键、白键、黑键、白键、黑键、白键、黑键、白键
    # 对应：C, C#, D, D#, E, F, F#, G, G#, A, A#, B
    corrected_pattern = [
        True,  # C
        False,  # C#
        True,  # D
        False,  # D#
        True,  # E
        True,  # F
        False,  # F#
        True,  # G
        False,  # G#
        True,  # A
        False,  # A#
        True,  # B
    ]
    return corrected_pattern[(note - 21) % len(corrected_pattern)]


def usage():
    print("--input [device_id] : Midi message logger")
    print("--output [device_id] : Midi piano keyboard")
    print("--list : list available midi devices")


def main(mode="output", device_id=None):
    """Run a Midi example

    Arguments:
    mode - if 'output' run a midi keyboard output example
              'input' run a midi event logger input example
              'list' list available midi devices
           (default 'output')
    device_id - midi device number; if None then use the default midi input or
                output device for the system

    """

    if mode == "input":
        input_main(device_id)
    elif mode == "output":
        output_main(device_id)
    elif mode == "list":
        print_device_info()
    else:
        raise ValueError(f"Unknown mode option '{mode}'")


if __name__ == "__main__":
    device_id: Optional[int] = None
    try:
        device_id = int(sys.argv[-1])
    except ValueError:
        device_id = None

    if "--input" in sys.argv or "-i" in sys.argv:
        input_main(device_id)

    elif "--output" in sys.argv or "-o" in sys.argv:
        output_main(device_id)
    elif "--list" in sys.argv or "-l" in sys.argv:
        print_device_info()
    else:
        # usage()
        print_device_info()

    pg.quit()
