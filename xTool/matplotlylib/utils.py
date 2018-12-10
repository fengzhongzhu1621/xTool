"""
Utility Routines for Working with Matplotlib Objects
====================================================
"""
import io
import base64

import matplotlib
from matplotlib.colors import colorConverter


def color_to_hex(color):
    """Convert matplotlib color code to hex color code"""
    if color is None or colorConverter.to_rgba(color)[3] == 0:
        return 'none'
    else:
        rgb = colorConverter.to_rgb(color)
        return '#{0:02X}{1:02X}{2:02X}'.format(*(int(255 * c) for c in rgb))


def many_to_one(input_dict):
    """Convert a many-to-one mapping to a one-to-one mapping"""
    return dict((key, val)
                for keys, val in input_dict.items()
                for key in keys)


def image_to_base64(image):
    """
    Convert a matplotlib image to a base64 png representation

    Parameters
    ----------
    image : matplotlib image object
        The image to be converted.

    Returns
    -------
    image_base64 : string
        The UTF8-encoded base64 string representation of the png image.
    """
    ax = image.axes
    binary_buffer = io.BytesIO()

    # image is saved in axes coordinates: we need to temporarily
    # set the correct limits to get the correct image
    lim = ax.axis()
    ax.axis(image.get_extent())
    image.write_png(binary_buffer)
    ax.axis(lim)

    binary_buffer.seek(0)
    return base64.b64encode(binary_buffer.read()).decode('utf-8')
