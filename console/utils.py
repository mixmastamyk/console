# -*- coding: future_fstrings -*-
'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018-2020, Mike Miller - Released under the LGPL, version 3+.

    This module contains cross-platform utility and convenience functions for
    use under ANSI-compatible terminals.

    See also:

        - `getpass <https://docs.python.org/3/library/getpass.html>`_
'''
import logging
import re
import sys, os
from time import sleep
from urllib.parse import quote

from .constants import BEL, OSC, ST
from .screen import sc
from .detection import is_a_tty, os_name, _read_clipboard
from .meta import defaults
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

        Returns: text sequence to be written, for testing.

        Note:
            Cursor position does not change.
    '''
    text = sc.erase_line(_mode_map.get(mode, mode))
    if _CHOSEN_PALETTE:
        _write(text)
    return text


def clear_lines(lines, mode=2):
    ''' Clear the given number of lines above.

        Arguments:
            lines: number of lines above to clear.
            mode:  | 0 | 'forward'  | 'right' - Clear cursor to end of line.
                   | 1 | 'backward' | 'left'  - Clear cursor to beginning of line.
                   | 2 | 'full'               - Clear entire line.

        Returns: text sequence to be written, for testing.
    '''
    mode = _mode_map.get(mode, mode)
    erase_cmd = sc.erase_line(mode)
    up_cmd = sc.up(1)
    commands = []

    for line in range(lines):
        commands.append(erase_cmd)
        commands.append(up_cmd)

    text = ''.join(commands)
    if _CHOSEN_PALETTE:
        _write(text)
    return text


def clear_screen(mode=2):
    ''' Clear the terminal/console screen. (Also aliased to clear.)

        Arguments:

            mode:  | 0 | 'forward'   - Clear cursor to end of screen, cursor stays.
                   | 1 | 'backward'  - Clear cursor to beginning of screen, ""
                   | 2 | 'full'      - Clear entire visible screen, cursor to 1,1.
                   | 3 | 'history'   - Clear entire visible screen and scrollback
                                       buffer (xterm).

        Returns: text sequence to be written, for testing.
    '''
    text = sc.erase(_mode_map.get(mode, mode))
    if _CHOSEN_PALETTE:
        _write(text)
    return text


def flash(seconds=.1):
    ''' Flash screen,
        i.e. turn on reverse video and back again,
        given a delay in floating-point seconds.
        This can be useful as a visible bell.

        Arguments:
            float seconds:  how long to wait in reverse video

        Returns: text sequence to be written, for testing.
    '''
    if _CHOSEN_PALETTE:
        _write(sc.reverse_video)
        sleep(seconds)
        _write(sc.normal_video)
        return sc.reverse_video + sc.normal_video  # for testing


def get_clipboard(source='c', encoding='utf8',
                  max_bytes=defaults.MAX_CLIPBOARD_SIZE, timeout=.2):
    ''' Read string or byte data from the clipboard.

        Arguments:
            data:  str
            source:  {c, p, q, s, 0-7}
                (clipboard, primary, secondary, selection, buffers 0-7)
            encoding: decode to unicode or pass None for bytes.
            max_bytes: minor impediment to sending too much text.

        Returns: data found

        Note:
            https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
            #h3-Operating-System-Commands
            Works on xterm, hterm.
    '''  # functionality in detection module:
    if _CHOSEN_PALETTE:
        return _read_clipboard(source=source, encoding=encoding,
                               max_bytes=max_bytes, timeout=timeout)


def make_hyperlink(target, caption=None, icon='', **params):
    ''' Returns a terminal hyperlink, given a link and caption text.

        Arguments:

            target:     Link to the destination, 'http://foo.bar/baz'
            caption:    Optional descriptive text, defaults to target, e.g.
                        'Click-en Sie hier!'
            icon:       Add link icon to end of text, e.g. icon='🔗'
            params:     Optional key word args, to be formatted as:
                        'id=xyz123:foo=bar:baz=quux'
                        (See note below.)

        Returns: text sequence to be written, caption, or empty string.

        Example::

            from console import fg, fx
            from console.utils import make_hyperlink

            link = make_hyperlink('ftp://ftp.netscape.com/…/navigator.tar.gz',
                                  'Blast from the past!')
            link_style = fg.blue + fx.underline
            print(link_style(link))  # in full effect

        Note: experimental, see below for details:
            https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda
    '''
    if _CHOSEN_PALETTE:
        MAX_URL = 2083  # spec recommendations
        MAX_VAL = 250
        SAFE_CHARS = (  # ''.join([ chr(n) for n in range(32, 126) ])
            ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            '[\\]^_`abcdefghijklmnopqrstuvwxyz{|}'
        )
        # sanity & security checks
        if caption is None:
            caption = target
        if params:
            tokens = []
            for key, val in params.items():
                if len(val) > MAX_VAL:
                    val = val[:MAX_VAL]
                for char in val:
                    if char in ('=', ':', ';'):
                        raise ValueError(f'illegal chars in val: {key}={val!r}')
                tokens.append(f'{key}={val}')
            params = ':'.join(tokens)

        if len(target) > MAX_URL:  # security limits
            target = target[:MAX_URL]

        target = quote(target, safe=SAFE_CHARS)  # url encode

        return f'{OSC}8;{params or ""};{target}{ST}{caption}{icon}{OSC}8;;{ST}'

    else:  # don't bother if redirected and/or ANSI disabled.
        return caption or ''


def notify_cwd(path=None):
    ''' Notify the terminal of the current working directory.

        Arguments:
            path:  str

        Returns: text sequence to be written, for testing.

        Notes:
            https://gitlab.freedesktop.org/terminal-wg/specifications/-/issues/20
            https://gitlab.com/gnachman/iterm2/-/issues/3939
    '''
    if not path:
        path = os.getcwd()

    # encode as url
    scheme = 'file://'
    if not path.startswith(scheme):
        path = scheme + path
    path = quote(path)
    text = f'{OSC}7;{path}{ST}'
    if _CHOSEN_PALETTE:
        _write(text)
    return text


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
        if _CHOSEN_PALETTE:
            _write(text)
        return text  # for testing


def set_clipboard(data, destination='c', encoding='utf8',
                  max_bytes=defaults.MAX_CLIPBOARD_SIZE):
    ''' Write string or byte data to the clipboard.

        Arguments:
            data: str or bytes
            destination:  {c, p, q, s, 0-7}
                (clipboard, primary, secondary, selection, buffers 0-7)
            encoding: if string is passed, encode to bytes
            max_bytes: minor impediment to sending too much text.

        Returns: text sequence to be written or None, for testing.

        Note:
            https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
            #h3-Operating-System-Commands
    '''
    if _CHOSEN_PALETTE:
        if len(data) > max_bytes:
            raise RuntimeError(f'clipboard data too large! ({len(data)} bytes)')

        from base64 import b64encode

        if isinstance(data, str):
            data = data.encode(encoding)
        if not isinstance(data, bytes):
            raise TypeError('data was not string or bytes: %s' % type(data))

        # all this needs to be in bytes
        payload = b64encode(data)
        envelope = f'{OSC}52;{destination};%b{ST}'.encode('ascii')
        text = envelope % payload

        # https://stackoverflow.com/a/908440/450917
        if hasattr(sys.stdout, 'buffer'):  # slightly more direct route
            sys.stdout.buffer.write(text)
            sys.stdout.flush()
        else:
            _write(text.decode('ascii'))  # bytes --> unicode --> bytes
        return text


def set_title(title, mode=0):
    ''' Set the title of the terminal window/tab/icon.

        Arguments:
            title:  str
            mode:  | 0 | 'both'   - Set icon/taskbar and window/tab title
                   | 1 | 'icon'   - Set only icon/taskbar title
                   | 2 | 'title'  - Set only window/tab title

        Returns: text sequence to be written or None, for testing.
    '''
    if os_name == 'nt':
        from .windows import set_title
        return set_title(title)
    else:
        if _CHOSEN_PALETTE:
            text = f'{OSC}{_title_mode_map.get(mode, mode)};{title}{BEL}' # ST?
            _write(text)
        return text


def strip_ansi(text, c1=False, osc=False):
    ''' Strip ANSI escape sequences from a portion of text.
        https://stackoverflow.com/a/38662876/450917

        Arguments:
            line: str
            osc: bool  - include OSC commands in the strippage.
            c1:  bool  - include C1 based commands in the strippage.

        Returns: stripped text

        Notes:
            Enabling both C1 and OSC stripping is less efficient and the two
            options can mildly conflict with one another.
            The less problematic order was chosen,
            but there may still be rare C1/OSC fragments left over.
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
    ''' Convenience - returns the length of a string minus escape sequences.

        Useful to find if a string will fit inside a given length on screen.
    '''
    return len(strip_ansi(text))


# shortcuts for convenience, compatibility:
clear = clear_screen
cls = reset_terminal


# -- wait key implementations ------------------------------------------------
if os_name == 'nt':
    from msvcrt import getwch as _get_char
elif os_name == 'posix':
    from .detection import _get_char


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
                key = _get_char()
                if key in keys:
                    return key
        else:
            return _get_char()


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
