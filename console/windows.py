# -*- coding: future_fstrings -*-
'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    Module for traditional Windows API crud (though not WSL).
    Typically, it is not necessary to use this module directly;
    the detection module is preferred.

    https://docs.microsoft.com/en-us/windows/console/console-reference
'''
import sys
import logging
try:
    from ctypes import (byref, c_short, c_ushort, c_long, Structure, windll,
                        create_unicode_buffer)
    from ctypes.wintypes import DWORD, HANDLE

    kernel32 = windll.kernel32
    # https://stackoverflow.com/a/17998333/450917
    kernel32.GetStdHandle.restype = HANDLE

except (ValueError, NameError, ImportError):
    # handle Sphinx import under Linux errors
    c_short = c_ushort = c_long = Structure = kernel32 = DWORD = windll = object

import env

from . import color_tables
from .meta import defaults
from .constants import TermLevel


# winbase.h constants
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12

BUILD_ANSI_AVAIL = 10586  # Win10 TH2, Nov 2015
_mask_map = dict(
    foreground=0x000f,
    fg=0x000f,
    background=0x00f0,
    bg=0x00f0,
)
_win_to_ansi_offset_map = {
    # conhost, ansi
     0:   0,   # BLACK,  :  black
     1:   4,   # BLUE,   :  red
     2:   2,   # GREEN,  :  green
     3:   6,   # CYAN,   :  yellow
     4:   1,   # RED,    :  blue
     5:   5,   # MAGENTA :  magenta/purple
     6:   3,   # YELLOW  :  cyan,
     7:   7,   # GREY,   :  gray

     8:   8,   # BLACK,  :  light black
     9:  12,   # BLUE,   :  light red
    10:  10,   # GREEN,  :  light green
    11:  14,   # CYAN,   :  light yellow
    12:   9,   # RED,    :  light blue
    13:  13,   # MAGENTA :  light magenta
    14:  11,   # YELLOW  :  light cyan
    15:  15,   # GREY,   :  light white
}

log = logging.getLogger(__name__)


class _COORD(Structure):
    ''' Struct from wincon.h. '''
    _fields_ = [
        ('X', c_short),
        ('Y', c_short),
    ]


class _SMALL_RECT(Structure):
    ''' Struct from wincon.h. '''
    _fields_ = [
        ('Left', c_short),
        ('Top', c_short),
        ('Right', c_short),
        ('Bottom', c_short),
    ]


class CONSOLE_SCREEN_BUFFER_INFO(Structure):
    ''' Struct from wincon.h. '''
    _fields_ = [
        ('dwSize', _COORD),
        ('dwCursorPosition', _COORD),
        ('wAttributes', c_ushort),
        ('srWindow', _SMALL_RECT),
        ('dwMaximumWindowSize', _COORD),
    ]


def add_os_sysexits():
    ''' Make the sysexit.h exit-status constants available under Windows. '''
    import os

    os.EX_OK            = 0     # successful termination
    # os.EX__BASE       = 64    # base value for error messages
    os.EX_USAGE         = 64    # command line usage error
    os.EX_DATAERR       = 65    # data format error
    os.EX_NOINPUT       = 66    # cannot open input
    os.EX_NOUSER        = 67    # addressee unknown
    os.EX_NOHOST        = 68    # host name unknown
    os.EX_UNAVAILABLE   = 69    # service unavailable
    os.EX_SOFTWARE      = 70    # internal software error
    os.EX_OSERR         = 71    # system error (e.g., can't fork)
    os.EX_OSFILE        = 72    # critical OS file missing
    os.EX_CANTCREAT     = 73    # can't create (user) output file
    os.EX_IOERR         = 74    # input/output error
    os.EX_TEMPFAIL      = 75    # temp failure; user is invited to retry
    os.EX_PROTOCOL      = 76    # remote error in protocol
    os.EX_NOPERM        = 77    # permission denied
    os.EX_CONFIG        = 78    # configuration error
    # EX__MAX           = 78    # maximum listed value


def cls():
    ''' Clear (reset) the console. '''
    # Clumsy but works - Win32 API takes 50 lines of code
    # and manually fills entire screen with spaces :/

    # https://docs.microsoft.com/en-us/windows/console/clearing-the-screen
    # https://github.com/tartley/colorama/blob/master/colorama/winterm.py#L111
    from subprocess import call
    call('cls', shell=True)


def detect_terminal_level(basic_palette=None):
    ''' Returns whether we think the terminal supports basic, extended, or
        direct color; None if not able to tell.  Windows variant.

        Returns:
            level:      None or TermLevel member
            color_sep   The extended color sequence separator character,
                        i.e. ":" or ";".
    '''
    ansicon = is_colorama = None
    _color_sep = env.PY_CONSOLE_COLOR_SEP or ';'  # supports only ; for now
    level = TermLevel.DUMB
    TERM = env.TERM.value or ''  # shortcut

    if TERM == 'alacritty':  # try to alleviate issue #8
        newfangled = True
    else:
        newfangled = is_ansi_capable() and all(enable_vt_processing())

    if newfangled:
        level = TermLevel.ANSI_DIRECT
    else:
        is_colorama = is_colorama_installed()
        ansicon = env.ANSICON.value

        if is_colorama or TERM.startswith('xterm'):
            level = TermLevel.ANSI_BASIC

        # upgrades
        if ansicon or TERM.endswith('-256color'):
            level = TermLevel.ANSI_EXTENDED

        if env.COLORTERM in ('truecolor', '24bit') or TERM == 'cygwin':
            level = TermLevel.ANSI_DIRECT

    log.debug(
        f'Term support: {level.name!r} (nt, TERM={TERM!r}, '
        f'COLORTERM={env.COLORTERM.value!r}, ANSICON={ansicon!r}, '
        f'colorama={is_colorama}, color_sep={_color_sep!r}) '
    )
    return level, _color_sep


def detect_unicode_support(codepage='cp65001'):  # aka utf8
    ''' Return whether unicode/utf8 is supported by the console/terminal. '''
    result = None
    if get_code_page() == codepage:
        result = True
    return result


def _find_basic_palette_from_os():
    ''' Find the platform-dependent 16-color basic palette—Windows version.

        This is used for "downgrading to the nearest color" support.
    '''
    if sys.getwindowsversion()[2] >= 16299: # new palette after Win10 1709 FCU
        pal_name = 'cmd_1709'
        basic_palette = color_tables.cmd1709_palette4
    else:
        pal_name = 'cmd_legacy'
        basic_palette = color_tables.cmd_palette4

    return pal_name, basic_palette


def enable_vt_processing():
    ''' What it says on the tin.

        - https://docs.microsoft.com/en-us/windows/console/setconsolemode
          #ENABLE_VIRTUAL_TERMINAL_PROCESSING

        - https://stackoverflow.com/q/36760127/450917

        Returns:
            Tuple of status codes from SetConsoleMode for (stdout, stderr).
    '''
    results = []

    for stream in (STD_OUTPUT_HANDLE, STD_ERROR_HANDLE):
        handle = kernel32.GetStdHandle(stream)
        # get current mode
        mode = DWORD()
        if not kernel32.GetConsoleMode(handle, byref(mode)):
            break

        # check if not set, then set
        if (mode.value & ENABLE_VIRTUAL_TERMINAL_PROCESSING) == 0:
            results.append(
                kernel32.SetConsoleMode(handle,
                            mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
            )
        else:
            results.append('Already Enabled')
    results = tuple(results)
    log.debug('%s %s', all(results), results)
    return results


def is_ansi_capable():
    ''' Check to see whether this version of Windows is recent enough to
        support "ANSI VT"" processing.
    '''
    try:
        CURRENT_VERS = sys.getwindowsversion()[:3]

        if CURRENT_VERS[2] > BUILD_ANSI_AVAIL:
            result = True
        else:
            result = False
        log.debug('%s (Windows version: %s > %s)',
                  result, CURRENT_VERS, BUILD_ANSI_AVAIL)
        return result
    except AttributeError:
        pass


def is_colorama_installed(stream=sys.stdout):
    '''  Detect if the colorama stream wrapper has been initialized. '''
    result = None
    try:
        import colorama
        if isinstance(stream, colorama.ansitowin32.StreamWrapper):
            result = True
        else:
            result = False
    except ImportError:
        pass
    log.debug('%s', result)
    return result


def get_code_page():
    '''  Return the code page for this console/terminal instance. '''
    from locale import getpreferredencoding
    return getpreferredencoding()


def get_color(name, number=None, timeout=None):
    ''' Query the default terminal for colors, etc.

        Arguments:
            name: str - one of ('foreground', 'fg', 'background', 'bg')

            number: compatibility only
            timeout: compatibility only

        Returns:
            tuple[str]: 
                A tuple of four-digit hex strings after parsing,
                the last two digits are the least significant and can be
                chopped when needed:

                ``('DEAD', 'BEEF', 'CAFE')``

                If an error occurs during retrieval or parsing,
                the tuple will be empty.

        Examples:
            >>> get_color('bg')
            ... ('0000', '0000', '0000')

            >>> get_color('index', 2)       # second color in indexed
            ... ('4e4d', '9a9a', '0605')    # palette, 2 aka 32 in basic

        Notes:
            On Windows, only able to find palette defaults,
            which may be different if they were customized.
    '''
    color = ()
    if name != 'index':
        # also applies to Windows Terminal
        color_id = get_color_id(name)
        if sys.getwindowsversion()[2] > 16299:  # Win10 FCU, new palette
            basic_palette = color_tables.cmd1709_palette4
        else:
            basic_palette = color_tables.cmd_palette4
        color = tuple(f'{i:02x}' for i in basic_palette[color_id]) # compat

    log.debug('%s %s color: %r', name, number, color)
    return color


def get_color_id(name, stream=STD_OUTPUT_HANDLE):
    ''' Returns current color ids of console.

        https://docs.microsoft.com/en-us/windows/console/getconsolescreenbufferinfo

        Arguments:
            name:   one of ('background', 'bg', 'foreground', 'fg')
            stream: Handle to stdout, stderr, etc.

        Returns:
            int:  a color id offset from the conhost palette.
                  Ids 8 and under are dark colors, above light.
                  Id numbers are converted to ANSI order.
    '''
    stream = kernel32.GetStdHandle(stream)
    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    kernel32.GetConsoleScreenBufferInfo(stream, byref(csbi))
    color_id = csbi.wAttributes & _mask_map.get(name, name)
    log.debug('color_id from conhost: %d', color_id)
    if name in ('background', 'bg'):
        color_id /= 16  # divide by 16
        log.debug('color_id divided: %d', color_id)

    # convert to ansi order
    color_id = _win_to_ansi_offset_map.get(color_id, color_id)
    log.debug('ansi color_id: %d', color_id)
    return color_id


def get_position(stream=STD_OUTPUT_HANDLE):
    ''' Returns current position of cursor, starts at 1. '''
    stream = kernel32.GetStdHandle(stream)
    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    kernel32.GetConsoleScreenBufferInfo(stream, byref(csbi))

    pos = csbi.dwCursorPosition
    # zero based, add ones for compatibility.
    return (pos.X + 1, pos.Y + 1)


def get_theme(timeout=defaults.READ_TIMEOUT):
    ''' Checks terminal for light/dark theme information.

        First checks for the environment variable COLORFGBG.
        Next, queries terminal, supported on Windows and xterm, perhaps others.
        See notes on get_color().

        Returns:
            str, None: 'dark', 'light', None if no information.
    '''
    theme = None
    log.debug('COLORFGBG: %s', env.COLORFGBG)
    if env.COLORFGBG:  # support this on Windows or not?
        FG, _, BG = env.COLORFGBG.partition(';')
        theme = 'dark' if BG < '8' else 'light'  # background wins

    else:
        color_id = get_color_id('background')
        theme = 'dark' if color_id < 8 else 'light'

    log.debug('%r', theme)
    return theme


def get_title(mode=None):
    ''' Returns console title string.

        https://docs.microsoft.com/en-us/windows/console/getconsoletitle
    '''
    MAX_LEN = 256
    buffer_ = create_unicode_buffer(MAX_LEN)
    kernel32.GetConsoleTitleW(buffer_, MAX_LEN)
    log.debug('%s', buffer_.value)
    return buffer_.value


def set_position(x, y, stream=STD_OUTPUT_HANDLE):
    ''' Sets current position of the cursor. '''
    stream = kernel32.GetStdHandle(stream)
    value = x + (y << 16)
    kernel32.SetConsoleCursorPosition(stream, c_long(value))


def set_title(title):
    ''' Set the console title. '''
    return kernel32.SetConsoleTitleW(title)
