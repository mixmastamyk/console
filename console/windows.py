'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    Module for Windows API crud.

    https://docs.microsoft.com/en-us/windows/console/console-reference
'''
try:
    from ctypes import (byref, c_short, c_ushort, Structure, windll,
                        create_unicode_buffer)
    from ctypes.wintypes import DWORD, HANDLE

    kernel32 = windll.kernel32
    # https://stackoverflow.com/a/17998333/450917
    kernel32.GetStdHandle.restype = HANDLE

except (ValueError, NameError, ImportError) as err:  # Sphinx import on Linux
    c_short = c_ushort = Structure = kernel32 = DWORD = windll = object


class COORD(Structure):
    ''' Struct from wincon.h. '''
    _fields_ = [
        ('X', c_short),
        ('Y', c_short),
    ]


class SMALL_RECT(Structure):
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
        ('dwSize', COORD),
        ('dwCursorPosition', COORD),
        ('wAttributes', c_ushort),
        ('srWindow', SMALL_RECT),
        ('dwMaximumWindowSize', COORD),
    ]


# winbase.h
ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12


_mask_map = dict(
    foreground=0x000f,
    fg=0x000f,
    background=0x00f0,
    bg=0x00f0,
)


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
    return tuple(results) or None  # last one only


def get_console_color(stream=STD_OUTPUT_HANDLE, mask='background'):
    ''' Returns current colors of console.

        https://docs.microsoft.com/en-us/windows/console/getconsolescreenbufferinfo
    '''
    stdout = kernel32.GetStdHandle(stream)
    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    kernel32.GetConsoleScreenBufferInfo(stdout, byref(csbi))
    color_id = csbi.wAttributes & _mask_map.get(mask, mask)

    return color_id


def get_console_title():
    ''' Returns console title via kernel32.GetConsoleTitleW()

        https://docs.microsoft.com/en-us/windows/console/getconsoletitle
    '''
    MAX_LEN = 256
    buffer_ = create_unicode_buffer(MAX_LEN)
    kernel32.GetConsoleTitleW(buffer_, MAX_LEN)
    return buffer_.value


def set_title(title):
    ''' Set the console title. '''
    return kernel32.SetConsoleTitleW(title)
