'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - ADDITIONAL PORTIONS released under the LGPL 3+.

    console.proximity
    ~~~~~~~~~~~~~~~~~~

    Given an 8-bit RGB color,
    find the closest extended 8-bit terminal color index.

    Nearest-color algorithm derived from:

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
from . import color_tables


color_table4 = []   # 16 colors
color_table8 = []   # 265 colors


def _build_color_table(base, extended=True):
    # start with first 16 colors
    color_table = []
    color_table.extend(base)  # handle tuples

    if extended:
        # colors 16..232: the 6x6x6 color cube
        valuerange = (0x00, 0x5f, 0x87, 0xaf, 0xd7, 0xff)

        for i in range(217):
            r = valuerange[(i // 36) % 6]
            g = valuerange[(i // 6) % 6]
            b = valuerange[i % 6]
            color_table.append((r, g, b))

        # colors 233..253: grayscale  # to 255!
        for i in range(1, 24):  # odd, this should go to 255, added 2 to range
            v = 8 + i * 10
            color_table.append((v, v, v))

    return color_table


def build_color_tables(base=color_tables.vga_palette4):
    '''
        Create the color tables for palette downgrade support,
        starting with the platform-specific 16 from the color tables module.
        Save as global state. :-/
    '''
    base = [] if base is None else base

    # make sure we have them before clearing
    table4 = _build_color_table(base, extended=False)
    if table4:
        color_table4.clear()
        color_table4.extend(table4)

    table8 = _build_color_table(base)
    if table8:
        color_table8.clear()
        color_table8.extend(table8)


def _euclidian_distance(color1, color2):
    ''' Euclid method - Sum of squares, to find distance

        Fast but poor approximation.

        "RGB color space is not orthogonal (straight)."
    '''
    rd = color1[0] - color2[0]
    gd = color1[1] - color2[1]
    bd = color1[2] - color2[2]

    return (rd * rd) + (gd * gd) + (bd * bd)


try:
    # CIEDE2000 - slow but better approximation
    # https://en.wikipedia.org/wiki/Color_difference#CIEDE2000
    from colorzero import Color
    from colorzero.deltae import ciede2000
    from colorzero.conversions import rgb_to_xyz, xyz_to_lab

    def _colorzero_ciede2000_distance(color1, color2):
        ''' Euclid method - Sum of squares, to find distance

            Fast but poor approximation.

            "RGB color space is not orthogonal (straight)."
        '''
        # avoid all the packaging, a bit faster
        other_color = xyz_to_lab(*rgb_to_xyz(color2[0]/255,
                                             color2[1]/255,
                                             color2[2]/255))
        return ciede2000(color1, other_color)

except ImportError:
    pass


def find_nearest_color_index(r, g, b, color_table=None, method='euclid'):
    ''' Given three integers representing R, G, and B,
        return the nearest color index.

        Arguments:
            r:    int - of range 0…255
            g:    int - of range 0…255
            b:    int - of range 0…255

        Returns:
            int, None: index, or None on error.
    '''
    shortest_distance = 257*257*3  # max eucl. distance from #000000 to #ffffff
    index = 0                      # default to black
    if not color_table:
        if not color_table8:
            build_color_tables()
        color_table = color_table8

    # prepare args
    if method == 'euclid':
        target_color = (r, g, b)
        find_distance_method = _euclidian_distance
    elif method == 'colorzero_ciede2000':
        target_color = Color.from_rgb_bytes(r, g, b).lab
        find_distance_method = _colorzero_ciede2000_distance

    for i, entry_rgb in enumerate(color_table):

        this_distance = find_distance_method(target_color, entry_rgb)

        if this_distance < shortest_distance:  # closer
            index = i
            shortest_distance = this_distance

    return index


def find_nearest_color_hexstr(hexdigits, color_table=None, method='euclid'):
    ''' Given a three or six-character hex digit string, return the nearest
        color index.

        Arguments:
            hexdigits:  a three/6 digit hex string, e.g. 'b0b'

        Returns:
            int, None: index, or None on error.
    '''
    triplet = []
    try:
        if len(hexdigits) == 3:
            for digit in hexdigits:
                digit = int(digit, 16)
                triplet.append((digit * 16) + digit)
        elif len(hexdigits) == 6:
            triplet.extend(int(hexdigits[i:i+2], 16) for i in (0, 2, 4))
        else:
            raise ValueError('wrong length: %r' % hexdigits)
    except ValueError:
        return None

    return find_nearest_color_index(*triplet,
                                    color_table=color_table,
                                    method=method)
