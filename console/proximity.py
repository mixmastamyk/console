'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - ADDITIONAL PORTIONS released under the LGPL 3+.

    console.proximity
    ~~~~~~~~~~~~~~~~~~

    Given an 8-bit RGB color,
    find the closest extended 8-bit terminal color index.

    Heavily derived from:

    .. code-block:: text

        pygments.formatters.terminal256
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        Formatter for 256-color terminal output with ANSI sequences.

        RGB-to-XTERM color conversion routines adapted from xterm256-conv
        tool (http://frexx.de/xterm-256-notes/data/xterm256-conv2.tar.bz2)
        by Wolfgang Frisch.

        :copyright: Copyright 2006-2017 by the Pygments team, see AUTHORS.
        :license: BSD, see LICENSE for details.
'''

_color_table = []


def _build_color_table():

    # colors 0..15: 16 basic colors, xterm palette
    _color_table.append((0x00, 0x00, 0x00))  # 0
    _color_table.append((0xcd, 0x00, 0x00))  # 1
    _color_table.append((0x00, 0xcd, 0x00))  # 2
    _color_table.append((0xcd, 0xcd, 0x00))  # 3
    _color_table.append((0x00, 0x00, 0xee))  # 4
    _color_table.append((0xcd, 0x00, 0xcd))  # 5
    _color_table.append((0x00, 0xcd, 0xcd))  # 6
    _color_table.append((0xe5, 0xe5, 0xe5))  # 7
    _color_table.append((0x7f, 0x7f, 0x7f))  # 8
    _color_table.append((0xff, 0x00, 0x00))  # 9
    _color_table.append((0x00, 0xff, 0x00))  # 10
    _color_table.append((0xff, 0xff, 0x00))  # 11
    _color_table.append((0x5c, 0x5c, 0xff))  # 12
    _color_table.append((0xff, 0x00, 0xff))  # 13
    _color_table.append((0x00, 0xff, 0xff))  # 14
    _color_table.append((0xff, 0xff, 0xff))  # 15

    # colors 16..232: the 6x6x6 color cube
    valuerange = (0x00, 0x5f, 0x87, 0xaf, 0xd7, 0xff)

    for i in range(217):
        r = valuerange[(i // 36) % 6]
        g = valuerange[(i // 6) % 6]
        b = valuerange[i % 6]
        _color_table.append((r, g, b))

    # colors 233..253: grayscale

    for i in range(1, 22):
        v = 8 + i * 10
        _color_table.append((v, v, v))


def find_nearest_color_index(r, g, b):
    ''' Given three integers representing R, G, and B,
        return the nearest color index.

        Arguments:
            r:    int - of range 0…255
            g:    int - of range 0…255
            b:    int - of range 0…255

        Returns:
            int, None: index, or None on error.
    '''
    distance = 257*257*3  # "infinity" (max distance from #000000 to #ffffff)
    index = 0

    for i in range(0, 254):
        values = _color_table[i]

        rd = r - values[0]
        gd = g - values[1]
        bd = b - values[2]

        this_distance = (rd * rd) + (gd * gd) + (bd * bd)

        if this_distance < distance:  # closer
            index = i
            distance = this_distance

    return index


def find_nearest_color_hexstr(hexdigits):
    ''' Given a three-character hex digit string, return the nearest color
        index.

        Arguments:
            hexdigits:  a three digit hex string, e.g. 'b0b'

        Returns:
            int, None: index, or None on error.
    '''
    try:
        triplet = []
        for digit in hexdigits:
            digit = int(digit, 16)
            triplet.append((digit * 16) + digit)
    except ValueError:
        return None

    return find_nearest_color_index(*triplet)


_build_color_table()
