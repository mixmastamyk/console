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
            mode:  0 - Clear cursor to right/end of line.
                   1 - Clear cursor to left/beginning of line.
                   2 - Clear entire line.

        Note:
            Cursor position does not change.
    '''
    text = screen.eraseline(mode)
    write(text)
    return text # for testing


def clear_screen(mode=2):
    ''' Clear the terminal screen. (Aliased to clear also)

        Arguments:
            mode:  0 - Clear cursor to end of screen, cursor stays.
                   1 - Clear cursor to beginning of screen, cursor stays.
                   2 - Clear entire visible screen, move cursor to 1, 1.
                   3 - Clear entire visible screen and scrollback buffer (xterm).
    '''
    write(screen.erase(mode))

clear = clear_screen


def reset_terminal():
    ''' Reset the terminal window. (Aliased to cls also)

        Greater than a fullscreen terminal clear, also clears the scrollback
        buffer.  May expose bugs in dumb terminals.

        TODO: add windows support.
    '''
    write(screen.reset)


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


def ansi_len(line):
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
