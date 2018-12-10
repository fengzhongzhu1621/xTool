#coding: utf-8
"""
colors
=====

Functions that manipulate colors and arrays of colors

There are three basic types of color types: rgb, hex and tuple:

rgb - An rgb color is a string of the form 'rgb(a,b,c)' where a, b and c are
floats between 0 and 255 inclusive.

hex - A hex color is a string of the form '#xxxxxx' where each x is a
character that belongs to the set [0,1,2,3,4,5,6,7,8,9,a,b,c,d,e,f]. This is
just the list of characters used in the hexadecimal numeric system.

tuple - A tuple color is a 3-tuple of the form (a,b,c) where a, b and c are
floats between 0 and 1 inclusive.

"""

def color_parser(colors, function):
    """
    将颜色格式化为另一种格式
    Takes color(s) and a function and applies the function on the color(s)

    In particular, this function identifies whether the given color object
    is an iterable or not and applies the given color-parsing function to
    the color or iterable of colors. If given an iterable, it will only be
    able to work with it if all items in the iterable are of the same type
    - rgb string, hex string or tuple

    """
    if isinstance(colors, str):
        return function(colors)

    if isinstance(colors, tuple) and isinstance(colors[0], Number):
        return function(colors)

    if hasattr(colors, '__iter__'):
        if isinstance(colors, tuple):
            new_color_tuple = tuple(function(item) for item in colors)
            return new_color_tuple

        else:
            new_color_list = [function(item) for item in colors]
            return new_color_list


def find_intermediate_color(lowcolor, highcolor, intermed):
    """
    返回两个颜色之间的中间颜色
    Returns the color at a given distance between two colors

    This function takes two color tuples, where each element is between 0
    and 1, along with a value 0 < intermed < 1 and returns a color that is
    intermed-percent from lowcolor to highcolor

    """
    diff_0 = float(highcolor[0] - lowcolor[0])
    diff_1 = float(highcolor[1] - lowcolor[1])
    diff_2 = float(highcolor[2] - lowcolor[2])

    inter_colors = (lowcolor[0] + intermed * diff_0,
                    lowcolor[1] + intermed * diff_1,
                    lowcolor[2] + intermed * diff_2)
    return inter_colors


def unconvert_from_RGB_255(colors):
    """
    将元组颜色转换为rgb
    Return a tuple where each element gets divided by 255

    Takes a (list of) color tuple(s) where each element is between 0 and
    255. Returns the same tuples where each tuple element is normalized to
    a value between 0 and 1

    """
    un_rgb_color = (colors[0]/(255.0),
                    colors[1]/(255.0),
                    colors[2]/(255.0))

    return un_rgb_color


def convert_to_RGB_255(colors):
    """
    Multiplies each element of a triplet by 255
    """
    return (colors[0]*255.0, colors[1]*255.0, colors[2]*255.0)


def label_rgb(colors):
    """
    Takes tuple (a, b, c) and returns an rgb color 'rgb(a, b, c)'
    """
    return ('rgb(%s, %s, %s)' % (colors[0], colors[1], colors[2]))


def unlabel_rgb(colors):
    """
    Takes rgb color(s) 'rgb(a, b, c)' and returns tuple(s) (a, b, c)

    This function takes either an 'rgb(a, b, c)' color or a list of
    such colors and returns the color tuples in tuple(s) (a, b, c)

    """
    str_vals = ''
    for index in range(len(colors)):
        try:
            float(colors[index])
            str_vals = str_vals + colors[index]
        except ValueError:
            if colors[index] == ',' or colors[index] == '.':
                str_vals = str_vals + colors[index]

    str_vals = str_vals + ','
    numbers = []
    str_num = ''
    for char in str_vals:
        if char != ',':
            str_num = str_num + char
        else:
            numbers.append(float(str_num))
            str_num = ''
    return (numbers[0], numbers[1], numbers[2])


def hex_to_rgb(value):
    """
    将十六进制的颜色转换为rgb元组
    Calculates rgb values from a hex color code.

    :param (string) value: Hex color string

    :rtype (tuple) (r_value, g_value, b_value): tuple of rgb values

    Example:

        '#FFFFFF' --> (255, 255, 255)

    """
    value = value.lstrip('#')
    hex_total_length = len(value)
    rgb_section_length = hex_total_length // 3
    return tuple(int(value[i:i + rgb_section_length], 16)
                 for i in range(0, hex_total_length, rgb_section_length))


def hex_to_rgb_2(value):
    """
    Change a hex color to an rgb tuple

    :param (str|unicode) value: The hex string we want to convert.
    :return: (int, int, int) The red, green, blue int-tuple.

    Example:

        '#FFFFFF' --> (255, 255, 255)

    """
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def colorscale_to_colors(colorscale):
    """
    Converts a colorscale into a list of colors
    """
    color_list = []
    for color in colorscale:
        color_list.append(color[1])
    return color_list
