'''
    console - An easy to use ANSI escape sequence library.
    © 2018, Mike Miller - Released under the LGPL, version 3+.

    This module contains utility and convenience functions for use under ANSI
    compatible terminals.
'''
import logging
import re

from .constants import OSC, BEL
from .screen import screen
from . import _DEBUG

ansi_pattern = re.compile(r'(\x9b|\x1b\[)[0-?]*[ -/]*[@-~]')
log = logging.getLogger(__name__)


if _DEBUG:  # TODO not getting set from demos, main?
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
    write(screen.eraseline(mode))


def clear_screen(mode=2):
    ''' Clear the terminal screen.

        Arguments:
            mode:  0 - Clear cursor to end of screen, cursor stays.
                   1 - Clear cursor to beginning of screen, cursor stays.
                   2 - Clear entire visible screen, move cursor to 1, 1.
                   3 - Clear entire visible screen and scrollback buffer (xterm).
    '''
    write(screen.erase(mode))


def reset_terminal():
    ''' Reset the terminal window.

        Greater than a fullscreen terminal clear, also clears the scrollback
        buffer.  May expose bugs in dumb terminals.
    '''
    write(screen.reset)


def set_title(title):
    ''' Set the title of the terminal window/tab. '''
    write(f'{OSC}2;{title}{BEL}')
    return title


def strip_ansi(line):
    ''' Strip ANSI escape sequences from a line of text.

        Probably doesn't handle OSC, as it has a right bracket.

        https://stackoverflow.com/a/38662876/450917
    '''
    return ansi_pattern.sub('', line)


def ansi_len(line):
    ''' Return the length of a string minus its ANSI escape sequences.

        Useful to find if a string will fit inside a given length on screen.
    '''
    return len(strip_ansi(line))


cls = reset_terminal
