'''
    console - An easy to use ANSI escape sequence library.
    © 2018, Mike Miller - Released under the LGPL, version 3+.
'''

from .style import fg, bg, fx, defx


fg, bg, fx, defx    # quiet pyflakes
_DEBUG = False


def _set_debug_mode(value):
    ''' Provides for more detailed output via logging functionality. '''
    global _DEBUG
    _DEBUG = bool(value)
