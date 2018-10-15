'''
    | console - Comprehensive utility library for ANSI terminals.
    | © 2018, Mike Miller - Released under the LGPL, version 3+.
'''
import sys

from .disabled import empty_bin as _empty_bin


_DEBUG = []  # mutable reference
_CHOSEN_PALETTE = None
fg = bg = fx = defx = sc = _empty_bin
__version__ = '0.92'


def set_debug_mode(value):
    ''' Provides for more detailed output via logging functionality. '''
    _DEBUG.clear()
    if value:
        _DEBUG.append(1)


# Py3.6+ - set up a dummy future-fstrings encoding that is really utf8
if sys.version_info >= (3, 6):
    import codecs
    import encodings

    _utf8 = encodings.search_function('utf8')
    _codec_map = {'future-fstrings': _utf8, 'future_fstrings': _utf8}
    codecs.register(_codec_map.get)


# detect palette, other modules are dependent
from .detection import TermStack, choose_palette as _choose_palette  # noqa

_CHOSEN_PALETTE = _choose_palette()
if _CHOSEN_PALETTE:
    # may now import other modules
    from .style import fg, bg, fx, defx
    from .screen import screen as sc

    fg, bg, fx, defx, sc, TermStack  # quiet pyflakes
