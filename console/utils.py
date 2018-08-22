'''
    console - Comprehensive escape sequence utility library for terminals.
    © 2018, Mike Miller - Released under the LGPL, version 3+.

    This module contains utility and convenience functions for use under ANSI
    compatible terminals.

    See also:

        - getpass
'''
import logging
import re

from .constants import OSC, BEL
from .screen import screen
from .detection import is_a_tty
from . import _DEBUG, _CHOSEN_PALETTE


ansi_seq_finder = re.compile(r'(\x9b|\x1b\[)[0-?]*[ -/]*[@-~]')
log = logging.getLogger(__name__)
_mode_map = dict(
    forward=0,
    backward=1,
    right=0,
    left=1,
    full=2,
    history=3,
)

if _DEBUG:  # TODO not getting set early enough
    def write(message):
        log.debug('%r', message)
        print(message, end='', flush=True)

else:
    def write(message):
        print(message, end='', flush=True)


def clear_line(mode=2):
    ''' Clear the current line.

        Arguments:
            mode:  0 | 'forward'  | 'right' - Clear cursor to end of line.
                   1 | 'backward' | 'left'  - Clear cursor to beginning of line.
                   2 | 'full'               - Clear entire line.

        Note:
            Cursor position does not change.
    '''
    text = screen.eraseline(_mode_map.get(mode, mode))
    write(text)
    return text  # for testing


def clear_screen(mode=2):
    ''' Clear the terminal screen. (Aliased to clear also)

        Arguments:
            mode:  0 | 'forward'   - Clear cursor to end of screen, cursor stays.
                   1 | 'backward'  - Clear cursor to beginning of screen, ""
                   2 | 'full'      - Clear entire visible screen, cursor to 1,1.
                   3 | 'history'   - Clear entire visible screen and scrollback
                                     buffer (xterm).
    '''
    text = screen.erase(_mode_map.get(mode, mode))
    write(text)
    return text  # for testing

clear = clear_screen


def reset_terminal():
    ''' Reset the terminal window. (Aliased to cls also)

        Greater than a fullscreen terminal clear, also clears the scrollback
        buffer.  May expose bugs in dumb terminals.

        TODO: add windows support.
    '''
    text = screen.reset
    write(text)
    return text  # for testing


def set_title(title):
    ''' Set the title of the terminal window/tab. '''
    if _CHOSEN_PALETTE:  # TODO: overridable?
        write(f'{OSC}2;{title}{BEL}')


def strip_ansi(line):
    ''' Strip ANSI escape sequences from a line of text.

        Probably doesn't handle OSC, as it has a right bracket.

        https://stackoverflow.com/a/38662876/450917
    '''
    return ansi_seq_finder.sub('', line)


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
    ''' Analogous to the DOS pause command, with a modifiable message.

        https://en.wikipedia.org/wiki/List_of_DOS_commands#PAUSE

        Returns:
            char or ESC - depending on key hit.
            None - immediately under i/o redirection, not an interactive tty.
    '''
    if is_a_tty():  # not sure if both of these should check
        print(message, end=' ', flush=True)
        return wait_key()
