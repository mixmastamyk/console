'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    Experimental terminfo support, under construction.

    Enables terminfo sequence lookup with console::

        import console.terminfo

    or use the environment variable::

        PY_CONSOLE_USE_TERMINFO=1

'''

try:
    from curses import setupterm, tigetstr

    setupterm()

    # ------------------------------------------------------
    from . import constants

    constants.BEL = tigetstr('bel')
    constants.BS = tigetstr('kbs')
    constants.CR = tigetstr('cr')
    constants.HT = tigetstr('ht')
    constants.LF = tigetstr('ind')

    # ------------------------------------------------------
    #~ from . import screen

    #~ Screen = screen.Screen

    #~ Screen.cuu = tigetstr('cuu')


except ModuleNotFoundError:

    raise ModuleNotFoundError('''Curses/terminfo not installed, see:
        - https://pypi.org/project/windows-curses/
        - https://www.lfd.uci.edu/~gohlke/pythonlibs/#curses
    ''')

