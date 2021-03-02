# -*- coding: future_fstrings -*-
'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    This module contains cross-platform utility and convenience functions for
    use under ANSI-compatible terminals.
    It is focused on Operating System Command (OSC) functionality and includes
    a few screen-based convenience functions.

    See also:

        - `getpass <https://docs.python.org/3/library/getpass.html>`_
'''
import logging
import re
import sys, os
from time import sleep
from urllib.parse import quote
from itertools import zip_longest, chain

from . import ansi_capable as _ansi_capable
from .constants import OSC, ST, _MODE_MAP, _TITLE_MODE_MAP
from .screen import sc
from .detection import (get_size, is_a_tty, os_name, _read_clipboard,
                        _sized_char_support)
from .meta import defaults


log = logging.getLogger(__name__)

ansi_csi0_finder = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')
ansi_csi1_finder = re.compile(r'\x9b[0-?]*[ -/]*[@-~]')

ansi_osc0_finder = re.compile(r'\x1b\].*?(\a|\x1b\\)')
ansi_osc1_finder = re.compile(r'\x9b.*?(\a|\x9d)')


def clear_line(mode=2):
    ''' Clear the current line.

        Arguments:

            mode: int | str

                   | 0 | 'forward'  | 'right' - Clear cursor to end of line.
                   | 1 | 'backward' | 'left'  - Clear cursor to beginning of line.
                   | 2 | 'full'               - Clear entire line.

        Returns: text sequence to be written, for testing.

        Note:
            Cursor position does not change.
    '''
    text = sc.clear_line(_MODE_MAP.get(mode, mode))
    if _ansi_capable:
        print(text, end='', flush=True)
    return text


def clear_lines(lines: int, mode=2):
    ''' Clear the given number of lines above.

        Arguments:
            lines: - number of lines above to clear.
            mode: int | str

                   | 0 | 'forward'  | 'right' - Clear cursor to end of line.
                   | 1 | 'backward' | 'left'  - Clear cursor to beginning of line.
                   | 2 | 'full'               - Clear entire line.

        Returns: text sequence to be written, for testing.
    '''
    mode = _MODE_MAP.get(mode, mode)
    erase_cmd = sc.clear_line(mode)
    up_cmd = sc.move_up(1)
    commands = []

    for line in range(lines):
        commands.append(erase_cmd)
        commands.append(up_cmd)

    text = ''.join(commands)
    if _ansi_capable:
        print(text, end='', flush=True)
    return text


def clear_screen(mode=2):
    ''' Clear the terminal/console screen. (Also aliased to clear.)

        Arguments:

            mode: int | str

                   | 0 | 'forward'   - Clear cursor to end of screen, cursor stays.
                   | 1 | 'backward'  - Clear cursor to beginning of screen, ""
                   | 2 | 'full'      - Clear entire visible screen, cursor to 1,1.
                   | 3 | 'history'   - Clear entire visible screen and scrollback
                                       buffer (xterm).

        Returns: text sequence to be written, for testing.
    '''
    text = sc.clear(_MODE_MAP.get(mode, mode))
    if _ansi_capable:
        print(text, end='', flush=True)
    return text


def flash(seconds=.1):
    ''' Flash screen, i.e. turn on reverse video and back again, given a delay
        in floating-point seconds. Useful as a visible bell.

        Arguments:
            seconds:  float - how long to wait in reverse video

        Returns: text sequence to be written, for testing.
    '''
    if _ansi_capable:
        print(sc.enable_flash, end='', flush=True)
        sleep(seconds)
        print(sc.disable_flash, end='', flush=True)
        return sc.enable_flash + sc.disable_flash  # for testing


def get_clipboard(source='c', encoding='utf8',
                  max_bytes=defaults.MAX_CLIPBOARD_SIZE, timeout=.2):
    ''' Read string or byte data from the clipboard.

        Arguments:
            source:  (int | str) of {c, p, q, s, 0-7}
                (clipboard, primary, secondary, selection, buffers 0-7)
            encoding: str - decode to unicode or pass None for bytes.
            max_bytes: int - minor impediment to sending too much text.
            timeout: float - seconds give up if answer not received in time.

        Returns: data found

        Note:
            Works on xterm, hterm, not many other terminals.
            https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
            #h3-Operating-System-Commands
    '''  # functionality in detection module:
    if _ansi_capable:
        return _read_clipboard(source=source, encoding=encoding,
                               max_bytes=max_bytes, timeout=timeout)


def make_hyperlink(target, caption=None, icon='',
        _max_url_len=defaults.MAX_URL_LEN, _max_val_len=defaults.MAX_VAL_LEN,
        **params,
    ):
    ''' Returns a terminal hyperlink, given a link and caption text.

        Arguments:

            target:     str. Link to the destination, 'http://foo.bar/baz'
            caption:    str | None
                        Optional descriptive text, defaults to target, e.g.
                        'Clicken Sie hier!'
            icon:       str Add link icon to end of text, e.g. icon='🔗'
            params:     str: str
                        Optional key word args, to be formatted as:
                        'id=xyz123:foo=bar:baz=quux'
                        (See note below.)
            _max_url_len, _max_val_len:  spec recommendations, see meta.py

        Returns: text sequence to be written, caption, or empty string.

        Example::

            from console import fg, fx
            from console.utils import make_hyperlink

            link = make_hyperlink('ftp://ftp.netscape.com/…/navigator.tar.gz',
                                  'Blast from the past!')
            link_style = fg.blue + fx.underline
            print(link_style(link))  # full effect https://youtu.be/BPcr1EDohiQ

        Note:
            This function doesn't print the escape sequence so it may be styled
            more easily.
            Experimental, see below for details:
             https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda
    '''
    if _ansi_capable:
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
                if len(val) > _max_val_len:
                    val = val[:_max_val_len]
                for char in val:
                    if char in ('=', ':', ';'):
                        raise ValueError(f'illegal chars in val: {key}={val!r}')
                tokens.append(f'{key}={val}')
            params = ':'.join(tokens)

        if len(target) > _max_url_len:  # security limits
            target = target[:_max_url_len]

        target = quote(target, safe=SAFE_CHARS)  # url encode
        return f'{OSC}8;{params or ""};{target}{ST}{caption}{icon}{OSC}8;;{ST}'

    else:  # don't bother if redirected and/or ANSI disabled.
        return caption or ''


def make_line(string='─', width=0, color=None, center=False, _fallback=80):
    ''' Build a header-rule style line, using Unicode characters.

        Arguments:
            string      A character or short string to repeat.
            color       A color name to assign to the line, defaults to dim.
            width       How long the line should be in characters,
                        defaults (zero) to full width of terminal.
            center      If a specific width is given, center it between spaces.

        New lines are handled by the caller.
        If the default width of the terminal is used,
        or center is given, no newline is necessary.
    '''
    auto_width = width < 1
    columns = get_size((_fallback, 0)).columns  # _fallback supports testing

    if auto_width:
        width = columns

    line = string * width
    if len(string) > 1:  # truncate line length if multi-char string
        line = line[:width]

    if center:
        if auto_width:  # manual width not set
            raise RuntimeError('center option needs a valid width.')
        else:
            num_spaces = (columns - width) // 2  # floor
            spacing = ' ' * num_spaces
            line = spacing + line + spacing

            # if result is short from floor, we'll need another space
            if len(line) != columns:
                line += ' '

    if _ansi_capable:
        from . import fg, fx
        if color:
            line = getattr(fg, color)(line)
        else:
            line = fx.dim(line)

    return line


def make_sized(text, double=True, wide=False):
    ''' Returns a sequence to print wide and/or double-sized text.
        Pertains to the whole line, doesn't reset to normal until a newline
        occurs.

        Arguments:
            text           The text to change size.
            double         Use the double-sized font.
            wide           Use the double-wide font.

        Note:

            - DEC sequences supported on xterm and Konsole, possibly others.
            - Double text is also wide so both options together are redundant.
              Wide therefore takes precedence.
    '''
    result = text
    if _ansi_capable and _sized_char_support:
        if wide:
            result =  f'\x1b#6{text}'  # DECDWL
        elif double:
            result = f'\x1b#3{text}\n\x1b#4{text}'  # DECDHL, DECDHL

    return result


def measure(start=1, limit=200, offset=0, newlines=True):
    ''' Returns a ruler-style line of measurement across the width of the
        terminal.  Each column number should be read top down::

            # ↓  Column 124
            ..1.
            ..2.
            ..4.

        Arguments:
            start           The number to start with, e.g. 0 or 1
            limit           The column to limit to or end at.
            offset          Number of spaces to push to the right.
            newlines        Whether to insert newlines after each line.
                            Not strictly needed but helps when the window is
                            cromulently embiggened.
        Note:

            This function for debugging, few apps will need it.
    '''
    from . import fg, bg, fx
    width = min(limit, get_size().columns)
    evn_style = fg.i236 + bg.i244
    odd_style = fg.i244 + bg.i236
    results = []

    for i in range(start, width + start):
        digits = str(i)
        styled_digits = []

        for j, digit in enumerate(digits):

            # style digit
            if not i % 10: # mult of 10
                digit = fx.reverse(digit)
            elif i % 2:  # odd
                digit = odd_style(digit)
            else:  # even
                digit = evn_style(digit)

            styled_digits.append(digit)

        results.append(styled_digits)

    if newlines:
        results.append('\n\n')

    # transpose and concatenate
    results = zip_longest(*results, fillvalue=' ')

    if offset:
        offset = ' ' * offset
        return ''.join(chain.from_iterable(  # prepend each line with offset
            chain(offset, result) for result in results
        ))
    else:
        return ''.join(chain.from_iterable(results))


def notify_cwd(path=None):
    ''' Notify the terminal of the current working directory. EXPERIMENTAL

        Arguments:
            path:  str

        Returns: text sequence to be written, for testing.

        Notes:
            https://gitlab.freedesktop.org/terminal-wg/specifications/-/issues/20
            https://conemu.github.io/en/AnsiEscapeCodes.html#OSC_Operating_system_commands
    '''
    if not path:
        path = os.getcwd()

    if os_name == 'nt':
        code = '9;9'
        path = f'"{path}"'
    else:
        code = '7'
        # encode as path as an url
        scheme = 'file://'
        if not path.startswith(scheme):
            path = scheme + path
        path = quote(path)

    text = f'{OSC}{code};{path}{ST}'
    if _ansi_capable:
        print(text, end='', flush=True)
    return text


def notify_message(message, title=''):
    ''' Notify the user with the given message. EXPERIMENTAL

        Arguments:
            message:  str
            title:    str     rxvt-unicode only.

        Returns: text sequence to be written, for testing.

        Notes:
            iterm2, rxvt with plugin, kitty
            https://gitlab.freedesktop.org/terminal-wg/specifications/-/issues/13
    '''
    if os.environ.get('TERM', '').startswith('rxvt'):
        code = '777'
        message = f'notify;{title};{message};'
    else:  # iterm2 style
        code = '9'

    text = f'{OSC}{code};{message}{ST}'
    if _ansi_capable:
        print(text, end='', flush=True)
    return text


if os_name == 'nt':

    def notify_cwd(path=None):
        ''' Notify the terminal of the current working directory. EXPERIMENTAL

            Arguments:
                path:  str

            Returns: text sequence to be written, for testing.

            Notes:
                https://conemu.github.io/en/AnsiEscapeCodes.html#OSC_Operating_system_commands
                https://gitlab.freedesktop.org/terminal-wg/specifications/-/issues/20
        '''
        if not path:
            path = os.getcwd()

        text = f'{OSC}9;9;"{path}"{ST}'
        if _ansi_capable:
            print(text, end='', flush=True)
        return text


    def notify_progress(value=None, error=False, indeterminate=False, paused=False):
        ''' Notify the terminal and user of the current progress,
            via the desktop taskbar.  EXPERIMENTAL

            Arguments:
                value:  int 0-100,  A value of 0 or 100 will disable the progress
                                    indicator.
                                    Outside this range will set error mode.
                error:  bool        Set explicitly.
                indeterminate: bool Set explicitly.
                paused:  bool       Set explicitly.

            Returns: text sequence to be written, for testing.

            Notes:
                Currently known to be useful only on Windows.
                Conflicts with iterm2 use of OSC9 for notifications.
                https://conemu.github.io/en/AnsiEscapeCodes.html#ConEmu_specific_OSC
                https://gitlab.freedesktop.org/terminal-wg/specifications/-/issues/29

        '''
        CLEAR, PROGRESS, ERROR, INDETERMINATE, PAUSED = range(5)  # modes
        mode = PROGRESS

        if error:  # error
            mode = ERROR  # Danger Will Robinson!
            value = 99
        elif indeterminate:
            mode = INDETERMINATE
            value = 0
        elif paused:
            mode = PAUSED
        elif value in (0, 100):
            mode = CLEAR
            value = 0
        elif value < 0 or value > 100:  # error
            mode = ERROR  # Danger!
            value = 99  # paint full bar red, 2 bytes

        text = f'{OSC}9;4;{mode};{value}{ST}'
        if _ansi_capable:
            print(text, end='', flush=True)
        return text

else:
    def notify_cwd(path=None):
        ''' Notify the terminal of the current working directory. EXPERIMENTAL

            Arguments:
                path:  str, do not url encode.

            Returns: text sequence to be written, for testing.

            Notes:
                https://gitlab.freedesktop.org/terminal-wg/specifications/-/issues/20
                https://conemu.github.io/en/AnsiEscapeCodes.html#OSC_Operating_system_commands
        '''
        if not path:
            path = os.getcwd()

        # encode as path as an url
        scheme = 'file://'
        if not path.startswith(scheme):
            path = scheme + path
        path = quote(path)

        text = f'{OSC}7;{path}{ST}'
        if _ansi_capable:
            print(text, end='', flush=True)
        return text


    def notify_progress(*args, **kwargs):
        ''' Function not implemented. '''
        raise NotImplementedError('only available on Windows.')


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
        if _ansi_capable:
            print(text, end='', flush=True)
        return text  # for testing


def set_clipboard(data, destination='c', encoding='utf8',
                  max_bytes=defaults.MAX_CLIPBOARD_SIZE):
    ''' Write string or byte data to the clipboard.

        Arguments:
            data: str | bytes
            destination:  (int | str) of {c, p, q, s, 0-7}
                (clipboard, primary, secondary, selection, buffers 0-7)
            encoding: str - if string is passed, encode to bytes
            max_bytes: int minor impediment to sending too much text.

        Returns: text sequence to be written or None, for testing.

        Note:
            Works on xterm, not many other terminals.
            https://invisible-island.net/xterm/ctlseqs/ctlseqs.html
            #h3-Operating-System-Commands
    '''
    if _ansi_capable:
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
            # bytes --> unicode --> bytes :-/
            print(text.decode('ascii'), end='', flush=True)
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
        set_title(title)  # returns a status code, not a string
    else:
        text = f'{OSC}{_TITLE_MODE_MAP.get(mode, mode)};{title}{ST}'
        if _ansi_capable:
            print(text, end='', flush=True)
        return text


def strip_ansi(text, c1=False, osc=False):
    ''' Strip ANSI escape sequences from a portion of text.
        https://stackoverflow.com/a/38662876/450917

        Arguments:
            line: str
            c1:  bool  - include C1 based commands in the strippage.
            osc: bool  - include OSC commands in the strippage.

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
cls = reset_terminal  # like DOS


# -- wait key implementations ------------------------------------------------
if os_name == 'nt':
    from msvcrt import getwch as _get_char
elif os_name == 'posix':
    from .detection import _get_char


def pause(message='Press any key to continue…', _return_key=False):
    ''' Analogous to the
        `DOS pause <https://en.wikipedia.org/wiki/List_of_DOS_commands#PAUSE>`_
        command from olden times, with a modifiable message.
        *"Where's the any key?"*

        Arguments:
            message:  str

        Returns:
            str, None:  One character or ESC - depending on key hit.
            None - immediately under i/o redirection, not an interactive tty.
    '''
    print(message, end=' ', flush=True)
    key = wait_key()

    print()
    if _return_key:  # for testing purposes; command shouldn't return it
        return key


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
