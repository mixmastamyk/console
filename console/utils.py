# -*- coding: future_fstrings -*-
'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    This module contains utility and convenience functions for use under ANSI
    compatible terminals.

    See also:

        - `getpass <https://docs.python.org/3/library/getpass.html>`_
'''
import logging
import re

from .constants import OSC, BEL
from .screen import sc
from .detection import is_a_tty, os_name
from . import _DEBUG, _CHOSEN_PALETTE


log = logging.getLogger(__name__)

ansi_csi0_finder = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')
ansi_csi1_finder = re.compile(r'\x9b[0-?]*[ -/]*[@-~]')

# ansi_osc0_finder = re.compile(r'(\x1b\][0-?]*\a?|\a)')  # TODO: leave title
ansi_osc0_finder = re.compile(r'\x1b\].*?(\a|\x1b\\)')
ansi_osc1_finder = re.compile(r'\x9b.*?(\a|\x9d)')

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

if _DEBUG:
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
    text = sc.erase_line(_mode_map.get(mode, mode))
    _write(text)
    return text  # for testing


def clear_screen(mode=2):
    ''' Clear the terminal/console screen. (Also aliased to clear.)

        Arguments:

            mode:  | 0 | 'forward'   - Clear cursor to end of screen, cursor stays.
                   | 1 | 'backward'  - Clear cursor to beginning of screen, ""
                   | 2 | 'full'      - Clear entire visible screen, cursor to 1,1.
                   | 3 | 'history'   - Clear entire visible screen and scrollback
                                       buffer (xterm).
    '''
    text = sc.erase(_mode_map.get(mode, mode))
    _write(text)
    return text  # for testing


def reset_terminal():
    ''' Reset the terminal/console screen. (Also aliased to cls.)

        Greater than a fullscreen terminal clear, also clears the scrollback
        buffer.  May expose bugs in dumb terminals.
    '''
    if os_name == 'nt':
        from .windows import cls
        cls()
    else:
        text = sc.reset
        _write(text)
        return text  # for testing


def set_title(title, mode=0):
    ''' Set the title of the terminal window/tab/icon.

        Arguments:
            title:  str
            mode:  | 0 | 'both'   - Set icon/taskbar and window/tab title
                   | 1 | 'icon'   - Set only icon/taskbar title
                   | 2 | 'title'  - Set only window/tab title
    '''
    if os_name == 'nt':
        from .windows import set_title
        return set_title(title)
    else:
        if _CHOSEN_PALETTE:
            text = f'{OSC}{_title_mode_map.get(mode, mode)};{title}{BEL}'
            _write(text)
            return text  # for testing


def strip_ansi(text, c1=False, osc=False):
    ''' Strip ANSI escape sequences from a portion of text.
        https://stackoverflow.com/a/38662876/450917

        Arguments:
            line: str
            osc: bool  - include OSC commands in the strippage.
            c1:  bool  - include C1 commands in the strippage.

        Notes:
            Enabling both c1 and osc stripping is less efficient and the two
            options can mildly conflict with one another.
            The less problematic order was chosen,
            but there may still be rare C1 OSC fragments left over.
    '''
    text = ansi_csi0_finder.sub('', text)
    if osc:
        text = ansi_osc0_finder.sub('', text)
    if c1:
        text = ansi_csi1_finder.sub('', text)  # go first, less destructive
        if osc:
            text = ansi_osc1_finder.sub('', text)
    return text


def len_stripped(text):
    ''' Return the length of a string minus its ANSI escape sequences.

        Useful to find if a string will fit inside a given length on screen.
    '''
    return len(strip_ansi(text))


# shortcuts for convenience, compatibility:
clear = clear_screen
cls = reset_terminal


# -- wait key implementations ------------------------------------------------
if os_name == 'nt':
    from msvcrt import getwch as _getch
elif os_name == 'posix':
    from .detection import _getch


def wait_key(keys=None):
    ''' Waits for a keypress at the console and returns it.

        Arguments:
            keys - if passed, wait for this specific key, e.g. 'Q', 'ESC'.
                   may be a tuple.
        Returns:
            char or ESC - depending on key hit.
            None - immediately under i/o redirection, not an interactive tty.
    '''
    if is_a_tty():
        if keys:
            if not isinstance(keys, tuple):
                keys = (keys,)
            while True:
                key = _getch()
                if key in keys:
                    return key
        else:
            return _getch()


def pause(message='Press any key to continue…'):
    ''' Analogous to the ancient
        `DOS pause <https://en.wikipedia.org/wiki/List_of_DOS_commands#PAUSE>`_
        command from olden times,
        with a modifiable message.
        *"Where's the any key?"*

        Arguments:
            message:  str

        Returns:
            str, None:  One character or ESC - depending on key hit.
            None - immediately under i/o redirection, not an interactive tty.
    '''
    key = None
    print(message, end=' ', flush=True)
    if is_a_tty():  # not sure if both of these should check
        key = wait_key()

    print()
    return key
