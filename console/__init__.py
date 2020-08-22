'''
    | console - Comprehensive utility library for ANSI terminals.
    | © 2018, Mike Miller - Released under the LGPL, version 3+.
'''
import sys as _sys

import env as _env

from .constants import TermLevel as _TermLevel
from .disabled import empty_bin as _empty_bin


_term_level = None
# Define pass-thru objects for streams/dumb terminals:
fg = bg = ul = fx = defx = sc = _empty_bin


# Py3.6+ - set up a dummy future-fstrings encoding that is really utf8
if _sys.version_info >= (3, 6):
    import codecs as _codecs
    import encodings as _encodings

    _utf8 = _encodings.search_function('utf8')
    _codec_map = {'future-fstrings': _utf8, 'future_fstrings': _utf8}
    _codecs.register(_codec_map.get)


# defer imports for proper ordering
from .detection import TermStack

if _env.PY_CONSOLE_AUTODETECT != '0':

    # detect palette, other modules are dependent
    from .detection import init as _init  # noqa

    _term_level = _init()

    if _term_level:  # may now import other modules
        # monochrome stuff first
        from .style import fx, defx
        from .screen import sc

        if _term_level > _TermLevel.ANSI_MONOCHROME:
            from .style import fg, bg, ul  # Yo Iz, let's do this…

    fg, bg, ul, fx, defx, sc, TermStack  # quiet pyflakes


# Experimental terminfo support, under construction
if _env.PY_CONSOLE_USE_TERMINFO.truthy:

    from . import terminfo
