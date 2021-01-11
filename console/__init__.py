'''
    | console - Comprehensive utility library for ANSI terminals.
    | © 2018, Mike Miller - Released under the LGPL, version 3+.
'''
import env as _env

from .constants import TermLevel as _TermLevel
from .disabled import empty_bin as _empty_bin


_term_level = None
# Define pass-thru palette objects for streams and dumb terminals:
fg = bg = ul = fx = defx = sc = _empty_bin


# Py3.6+ - set up a dummy future-fstrings encoding that is really utf8
#~ import sys as _sys
#~ if _sys.version_info >= (3, 6):
# issue #12 - lets install it if need be, to be removed in a later version
try:
    from codecs import lookup as _lookup
    _lookup('future-fstrings')
except LookupError:
    import codecs as _codecs
    import encodings as _encodings

    _utf8 = _encodings.search_function('utf8')
    _codec_map = {'future-fstrings': _utf8, 'future_fstrings': _utf8}
    _codecs.register(_codec_map.get)


# defer imports for proper ordering
from .detection import TermStack


# detection defaults to True if not explicitly disabled
if (_env.PY_CONSOLE_AUTODETECT.value is None or
    _env.PY_CONSOLE_AUTODETECT.truthy):

    # detect palette, other modules are dependent
    from .detection import init as _init

    _term_level = _init()

    if _term_level:  # may now import other modules
        # monochrome stuff first
        from .style import fx, defx
        from .screen import sc
        from .detection import is_fbterm as _is_fbterm

        if _term_level > _TermLevel.ANSI_MONOCHROME:
            from .style import fg, bg  # Yo Iz, let's do this…

        # curly or colored underlines not handled well by linux consoles:
        if _term_level > _TermLevel.ANSI_BASIC and not _is_fbterm:
            from .style import ul
        else:
            fx.curly_underline = fx.underline  # downgrade

    fg, bg, ul, fx, defx, sc, TermStack  # quiet pyflakes


# Experimental terminfo support, under construction
if _env.PY_CONSOLE_USE_TERMINFO.truthy:

    from . import terminfo
    terminfo  # quiet pyflakes
