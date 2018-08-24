'''
    | console - Comprehensive escape sequence utility library for terminals.
    | © 2018, Mike Miller - Released under the LGPL, version 3+.
'''
import sys


_DEBUG = False


def _set_debug_mode(value):
    ''' Provides for more detailed output via logging functionality. '''
    global _DEBUG
    _DEBUG = bool(value)


# detect running as a script, e.g. demos, constants
if sys.argv and sys.argv[0] == '-m':  # try __loader__
    pass  # do nothing

else:

    # detect palette, other modules dependent
    from .detection import TermStack, choose_palette as _choose_palette

    _CHOSEN_PALETTE = _choose_palette()

    # now we can import other modules
    from .style import fg, bg, fx, defx
    from .screen import screen as sc

    fg, bg, fx, defx, sc, TermStack  # quiet pyflakes
