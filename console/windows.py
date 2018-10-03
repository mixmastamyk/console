'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    Module for Windows API crud.
'''
from ctypes import windll, wintypes, Structure, c_short, c_ushort, byref

SHORT = c_short
WORD = c_ushort


class COORD(Structure):
  """struct in wincon.h."""
  _fields_ = [
    ("X", SHORT),
    ("Y", SHORT)]


class SMALL_RECT(Structure):
  """struct in wincon.h."""
  _fields_ = [
    ("Left", SHORT),
    ("Top", SHORT),
    ("Right", SHORT),
    ("Bottom", SHORT)]


class CONSOLE_SCREEN_BUFFER_INFO(Structure):
  """struct in wincon.h."""
  _fields_ = [
    ("dwSize", COORD),
    ("dwCursorPosition", COORD),
    ("wAttributes", WORD),
    ("srWindow", SMALL_RECT),
    ("dwMaximumWindowSize", COORD)]


# winbase.h
STD_INPUT_HANDLE = -10
STD_OUTPUT_HANDLE = -11
STD_ERROR_HANDLE = -12

_GetConsoleScreenBufferInfo = windll.kernel32.GetConsoleScreenBufferInfo

_mask_map = dict(
    foreground=0x000f,
    fg=0x000f,
    background=0x00f0,
    bg=0x00f0,
)


def get_console_color(stream, mask='background'):
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
