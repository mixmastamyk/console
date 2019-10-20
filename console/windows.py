'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    Module for Windows API crud.

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

except (ValueError, NameError, ImportError):  # Sphinx import on Linux
    c_short = c_ushort = c_long = Structure = kernel32 = DWORD = windll = object


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


def cls():
    ''' Clear (reset) the console. '''
    # Clumsy but works - Win32 API takes 50 lines of code
    # and manually fills entire screen with spaces :/

    # https://docs.microsoft.com/en-us/windows/console/clearing-the-screen
    # https://github.com/tartley/colorama/blob/master/colorama/winterm.py#L111
    from subprocess import call
    call('cls', shell=True)


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
    log.debug('%s', results)
    return results


def is_ansi_capable():
    ''' Check to see whether this version of Windows is recent enough to
        support "ANSI VT"" processing.
    '''
    CURRENT_VERS = sys.getwindowsversion()[:3]

    if CURRENT_VERS[2] > BUILD_ANSI_AVAIL:
        result = True
    else:
        result = False
    log.debug('%s (Windows version: %s)', result, CURRENT_VERS)
    return result


def is_colorama_initialized():
    result = None
    try:
        import sys, colorama
        if isinstance(sys.stdout, colorama.ansitowin32.StreamWrapper):
            result = True
        else:
            result = False
    except ImportError:
        pass
    log.debug('%s', result)
    return result


def get_color(name, stream=STD_OUTPUT_HANDLE):
    ''' Returns current colors of console.

        https://docs.microsoft.com/en-us/windows/console/getconsolescreenbufferinfo

        Arguments:
            name:   one of ('background', 'bg', 'foreground', 'fg')
            stream: Handle to stdout, stderr, etc.

        Returns:
            int:  a color id from the conhost palette.
                  Ids under 0x8 (8) are dark colors, above light.
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


def set_position(x, y, stream=STD_OUTPUT_HANDLE):
    ''' Sets current position of the cursor. '''
    stream = kernel32.GetStdHandle(stream)
    value = x + (y << 16)
    kernel32.SetConsoleCursorPosition(stream, c_long(value))


def get_title():
    ''' Returns console title string.

        https://docs.microsoft.com/en-us/windows/console/getconsoletitle
    '''
    MAX_LEN = 256
    buffer_ = create_unicode_buffer(MAX_LEN)
    kernel32.GetConsoleTitleW(buffer_, MAX_LEN)
    log.debug('%s', buffer_.value)
    return buffer_.value


def set_title(title):
    ''' Set the console title. '''
    return kernel32.SetConsoleTitleW(title)
