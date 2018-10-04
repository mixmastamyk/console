'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    Module for Windows API crud.

    https://docs.microsoft.com/en-us/windows/console/console-reference
'''
try:
    import ctypes
    from ctypes import byref, c_short, c_ushort, windll, wintypes, Structure
    SHORT = c_short
    WORD = c_ushort
    _GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo

except (ValueError, NameError) as err:  # Sphinx import on Linux
    SHORT = WORD = Structure = _GetConsoleScreenBufferInfo = object


class COORD(Structure):
    ''' Struct from wincon.h. '''
    _fields_ = [
        ('X', SHORT),
        ('Y', SHORT),
    ]


class SMALL_RECT(Structure):
    ''' Struct from wincon.h. '''
    _fields_ = [
        ('Left', SHORT),
        ('Top', SHORT),
        ('Right', SHORT),
        ('Bottom', SHORT),
    ]


class CONSOLE_SCREEN_BUFFER_INFO(Structure):
    ''' Struct from wincon.h. '''
    _fields_ = [
        ('dwSize', COORD),
        ('dwCursorPosition', COORD),
        ('wAttributes', WORD),
        ('srWindow', SMALL_RECT),
        ('dwMaximumWindowSize', COORD),
    ]


# winbase.h
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


def get_console_color(stream=STD_OUTPUT_HANDLE, mask='background'):
    ''' Returns current colors of console.

        https://docs.microsoft.com/en-us/windows/console/getconsolescreenbufferinfo
    '''
    # https://stackoverflow.com/a/17998333/450917
    windll.kernel32.GetStdHandle.restype = wintypes.HANDLE

    stdout = windll.kernel32.GetStdHandle(stream)
    csbi = CONSOLE_SCREEN_BUFFER_INFO()
    _GetConsoleScreenBufferInfo(stdout, byref(csbi))
    color_id = csbi.wAttributes & _mask_map.get(mask, mask)

    return color_id


def get_console_title():
    ''' Returns console title via kernel32.GetConsoleTitleW()

        https://docs.microsoft.com/en-us/windows/console/getconsoletitle
    '''
    MAX_LEN = 256
    buffer_ = ctypes.create_unicode_buffer(MAX_LEN)
    windll.kernel32.GetConsoleTitleW(buffer_, MAX_LEN)
    return buffer_.value


def set_title(title):
    ''' Set the console title. '''
    return windll.kernel32.SetConsoleTitleW(title)
