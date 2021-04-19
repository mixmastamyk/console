'''
    | console - Comprehensive utility library for ANSI terminals.
    | © 2018-2021, Mike Miller - Released under the LGPL, version 3+.
'''
import env as _env

from .disabled import empty_bin as _empty_bin, empty_scr_bin as _empty_scr_bin


term_level = ansi_capable = using_terminfo = None
# Define pass-thru palette objects for streams and dumb terminals:
fg = bg = ul = fx = defx = _empty_bin
sc = _empty_scr_bin


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


# Early terminfo support
if _env.PY_CONSOLE_USE_TERMINFO.truthy or _env.SSH_CLIENT:
    try:
        import curses as _curses
        # a stub terminfo may have been installed with curses on windows, check
        from os import name as _os_name
        if _os_name == 'nt':
            from _curses import tigetstr as _tigetstr
            _curses.setupterm()
            if not _tigetstr('cr'):  # supports carriage return
                raise ImportError('this curses has a bum terminfo…')
    except ImportError:
        try:
            import jinxed as _curses
        except ImportError:
            raise ImportError(
                'terminfo not available, try installing ncurses.'
                ' On Windows, install the package from PyPI named "jinxed".'
            )
    _curses.setupterm()
    using_terminfo = True


# defer imports for proper ordering, read using_terminfo
from .constants import TermLevel as _TermLevel
from .detection import TermStack


# detection is performed if not explicitly disabled
if (_env.PY_CONSOLE_AUTODETECT.value is None or
    _env.PY_CONSOLE_AUTODETECT.truthy):

    # detect palette, other modules are dependent
    from .detection import init as _init

    term_level = _init(using_terminfo=using_terminfo)

    if term_level:  # > 0, may now import other modules
        ansi_capable = True  # simplify comparisons
        # monochrome stuff first
        from .style import fx, defx
        from .screen import sc
        from .detection import is_fbterm as _is_fbterm

        if term_level > _TermLevel.ANSI_MONOCHROME:
            from .style import fg, bg  # Yo Iz, let's do this…

        # curly or colored underlines not handled well by linux consoles:
        if term_level > _TermLevel.ANSI_BASIC and not _is_fbterm:
            from .style import ul
        else:
            fx.curly_underline = fx.underline  # downgrade
    else:
        ansi_capable = False  # simplify comparisons

    fg, bg, ul, fx, defx, sc, TermStack  # quiet pyflakes
