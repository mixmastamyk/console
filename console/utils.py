'''
    .. console - Comprehensive escape sequence utility library for terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    This module contains utility and convenience functions for use under ANSI
    compatible terminals.

    See also:

        - `getpass <https://docs.python.org/3/library/getpass.html>`_
'''
import logging
import re

from .constants import OSC, BEL
from .screen import screen
from .detection import is_a_tty
from . import _DEBUG, _CHOSEN_PALETTE


log = logging.getLogger(__name__)
# might be useful for these to be public:
ansi_csi_finder = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')   # no C1
ansi_osc_finder = re.compile(r'(\x1b\][0-?]*\007?|\007)')  # leave title

_mode_map = dict(
    forward=0,
    backward=1,
    right=0,
    left=1,
    full=2,
    history=3,
)
_title_mode_map = dict(
    both=0,
    icon=1,
    title=2,
)

if _DEBUG:  # TODO not getting set early enough
    def _write(message):
        log.debug('%r', message)
        print(message, end='', flush=True)

else:
    def _write(message):
        print(message, end='', flush=True)


def clear_line(mode=2):
    ''' Clear the current line.

        Arguments:

            mode:  | 0 | 'forward'  | 'right' - Clear cursor to end of line.
                   | 1 | 'backward' | 'left'  - Clear cursor to beginning of line.
                   | 2 | 'full'               - Clear entire line.

        Note:
            Cursor position does not change.
    '''
    text = screen.eraseline(_mode_map.get(mode, mode))
    _write(text)
    return text  # for testing


def clear_screen(mode=2):
    ''' Clear the terminal screen. (Aliased to clear also)

        Arguments:

            mode:  | 0 | 'forward'   - Clear cursor to end of screen, cursor stays.
                   | 1 | 'backward'  - Clear cursor to beginning of screen, ""
                   | 2 | 'full'      - Clear entire visible screen, cursor to 1,1.
                   | 3 | 'history'   - Clear entire visible screen and scrollback buffer (xterm).
    '''
    text = screen.erase(_mode_map.get(mode, mode))
    _write(text)
    return text  # for testing

clear = clear_screen


def reset_terminal():
    ''' Reset the terminal window. (Aliased to cls also)

        Greater than a fullscreen terminal clear, also clears the scrollback
        buffer.  May expose bugs in dumb terminals.

        TODO: add windows support.
    '''
    text = screen.reset
    _write(text)
    return text  # for testing


def set_title(title, mode=0):
    ''' Set the title of the terminal window/tab/icon.

        Arguments:
            title:  str
            mode:  | 0 | 'both'   - Set icon/taskbar and window/tab title
                   | 1 | 'icon'   - Set icon/taskbar title
                   | 2 | 'title'  - Set window/tab title
    '''
    if _CHOSEN_PALETTE:  # TODO: all overridable
        text = f'{OSC}{_title_mode_map.get(mode, mode)};{title}{BEL}'
        _write(text)
        return text  # for testing


def strip_ansi(line, osc=False):
    ''' Strip ANSI escape sequences from a line of text.
        https://stackoverflow.com/a/38662876/450917

        Arguments:
            line: str
            osc: bool  - include OSC commands in the strippage.

        Notes:
            Does not currently support the so-called C1 8-bit sequences,
            but could be improved:

                - ESC [   - Control Sequence Introducer (CSI  is 0x9b).
                - ESC \   - String Terminator (ST  is 0x9c).
                - ESC ]   - Operating System Command (OSC is 0x9d).
    '''
    line = ansi_csi_finder.sub('', line)
    if osc:
        line = ansi_osc_finder.sub('', line)
    return line


def len_stripped(line):
    ''' Return the length of a string minus its ANSI escape sequences.

        Useful to find if a string will fit inside a given length on screen.
    '''
    return len(strip_ansi(line))


cls = reset_terminal


# -- wait key implementations ------------------------------------------------
try:
    from msvcrt import getch as _getch  # Win32
except ImportError:                     # UNIX
    from .detection import _getch


def wait_key():
    ''' Waits for a keypress at the console and returns it.
        "Where's the any key?"

        Returns:
            char or ESC - depending on key hit.
            None - immediately under i/o redirection, not an interactive tty.
    '''
    if is_a_tty():
        return _getch()


def pause(message='Press any key to continue…'):
    ''' Analogous to the ancient
        `DOS pause <https://en.wikipedia.org/wiki/List_of_DOS_commands#PAUSE>`_
        command, with a modifiable message.

        Arguments:
            message:  str

        Returns:
            str, None:  One character or ESC - depending on key hit.
            None - immediately under i/o redirection, not an interactive tty.
    '''
    if is_a_tty():  # not sure if both of these should check
        print(message, end=' ', flush=True)
        return wait_key()
