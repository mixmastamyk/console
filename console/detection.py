# -*- coding: future_fstrings -*-
'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    This module contains capability detection routines for use under ANSI
    compatible terminals.  Most functions return None when not able to detect
    requested information.
'''
import sys, os
import logging

import env

from . import color_tables
from console.color_tables import DEFAULT_BASIC_PALETTE, term_palette_map
from .constants import (BS, BEL, CSI, ESC, ENQ, OSC, RS, ST, TermLevel,
                        _COLOR_CODE_MAP)
from .meta import __version__, defaults


TERMS_DIRECT_COLON = ('xterm-', 'iterm2-', 'kitty-', 'mintty-', 'mlterm-')
color_sep = ';'  # the above prefer to use colons as the direct color separator
termios = tty = None

is_fbterm = (env.TERM == 'fbterm')
is_xterm = env.XTERM_VERSION.bool  # the real thing
log = logging.getLogger(__name__)
os_name = os.name  # frequent use
_sized_char_support = is_xterm or env.TERM.startswith('konsole')


if os_name == 'posix':  # Tron leotards
    import termios, tty


class TermStack:
    ''' Context Manager to save, temporarily modify, then restore terminal
        attributes.  POSIX only.

        Arguments::
            stream      - The file object to operate on, defaulting to stdin.
            exit_mode   - Mode to exit with: now, drain, or flush default.

        Raises:
            AttributeError: when stream has no attribute 'fileno'

        Example:
            A POSIX implementation of get char/key::

                import tty

                with TermStack() as fd:
                    tty.setraw(fd)
                    print(sys.stdin.read(1))
    '''
    def __init__(self, stream=sys.stdin, exit_mode='flush'):
        if not termios:
            raise EnvironmentError('The termios module was not loaded, is '
                                   'this a POSIX-compatible environment?')
        self.fd = stream.fileno()
        self._exit_mode = exit_mode.upper()

    def __enter__(self):
        # save
        self._orig_attrs = termios.tcgetattr(self.fd)
        return self.fd

    def __exit__(self, *args):
        # restore
        mode = getattr(termios, f'TCSA{self._exit_mode}')
        termios.tcsetattr(self.fd, mode, self._orig_attrs)


def init(using_terminfo=False, _stream=sys.stdout, _basic_palette=()):
    ''' Automatically determine whether to enable ANSI sequences, and if so,
        what level of functionality is available.
        Takes a number of factors into account, e.g.:

        - Whether output stream is a TTY.
        - User preference environment variables:

            - ``CLICOLOR``, ``CLICOLOR_FORCE``, NO_COLOR``

        - Detection results:

            - The terminfo database, if requested or run remotely via SSH.

            - Or a further inspection of the environment:

                - ``TERM``, ``ANSICON``, ``COLORTERM`` configuration variables
                - Are standard output streams wrapped by colorama on Windows?

        Arguments:
            using_terminfo:     2B || !2B  # that is the question…
            _stream:            Which output file to check: stdout, stderr
            _basic_palette:     Force the platform-dependent 16 color palette,
                                for testing.  Tuple of 16 rgb-int tuples.
        Returns:
            level:              None or TermLevel member

        Note:
            This is the main function of the module—meant to be used unless
            requirements are more specific.
    '''
    level = pal_name = webcolors = None
    log.debug('console package, version: %s', __version__)
    log.debug('os.name/sys.platform: %s/%s', os_name, sys.platform)
    log.debug('using_terminfo: %s', using_terminfo)

    # find terminal capability level - given preferences and environment
    if color_is_forced() or (not color_is_disabled() and is_a_tty(stream=_stream)):
        global color_sep  # makes available

        if using_terminfo:
            if (not env.PY_CONSOLE_USE_TERMINFO.truthy  # set via ssh, not manually
                and env.LC_TERMINAL == 'iTerm2'):  # a recent iterm
                log.debug('ssh under iTerm2, skipping terminfo detection.')
                level, color_sep = TermLevel.ANSI_DIRECT, ':'  # upgrayyed
            else:
                level, color_sep = detect_terminal_level_terminfo()
            if level >= TermLevel.ANSI_BASIC:
                pal_name, _basic_palette = _find_basic_palette_from_term(env.TERM)

        if level is None:  # didn't occur, fall back to platform inspection
            level, color_sep = detect_terminal_level()

        if level >= TermLevel.ANSI_DIRECT:  # check for webcolors
            try: import webcolors
            except ImportError: pass
        log.debug(f'webcolors: {bool(webcolors)}')

        # find the platform-dependent 16-color basic palette
        if level and not using_terminfo:
            pal_name, _basic_palette = _find_basic_palette_from_os()

        log.debug('Basic palette: %r %r', pal_name, _basic_palette)
        if _basic_palette:
            from .proximity import build_color_tables
            build_color_tables(_basic_palette)  # for color downgrade

    level = level or TermLevel.DUMB
    log.debug('%s is available', level.name)
    return level


def color_is_disabled(**envars):
    ''' Look for clues in environment, e.g.:

        - https://bixense.com/clicolors/
        - http://no-color.org/

        Arguments:
            envars:     Additional environment variables to check for
                        equality, i.e. ``MYAPP_COLOR_DISABLED='1'``

        Returns:
            disabled:   None or bool
    '''
    result = None
    if 'NO_COLOR' in env:
        result = True
    elif env.CLICOLOR == '0':
        result = True
    elif env.CLICOLOR:
        result = False

    log.debug('color_disabled: %r (NO_COLOR=%s, CLICOLOR=%s)',
        result, env.NO_COLOR or None, env.CLICOLOR or None,
    )
    # check custom variables
    for name, value in envars.items():
        envar = getattr(env, name)
        if envar.value == value:
            result = True
        log.debug('%s == %r: %r', name, value, result)

    return result


def color_is_forced(**envars):
    ''' Look for clues in environment, e.g.:

        - https://bixense.com/clicolors/

        Arguments:
            envars:     Additional environment variables as keyword arguments
                        to check for equality, i.e. ``MYAPP_COLOR_FORCED='1'``
        Returns:
            forced:     bool
    '''
    result = env.CLICOLOR_FORCE and (env.CLICOLOR_FORCE != '0')
    log.debug('color_forced: %s (CLICOLOR_FORCE=%s)', result or None,
              env.CLICOLOR_FORCE or None)

    # check custom variables
    for name, value in envars.items():
        envar = getattr(env, name)
        if envar.value == value:
            result = True
        log.debug('%s == %r: %r', name, value, result)

    return result


def detect_terminal_level():
    ''' Returns whether we think the terminal is dumb or supports basic,
        extended, or direct color sequences.  posix version.

        This implementation looks at common environment variables,
        rather than terminfo.

        Returns:
            level:      None or TermLevel member
            color_sep   The extended color sequence separator character,
                        i.e. ":" or ";".
    '''
    level = TermLevel.DUMB
    TERM = env.TERM.value or ''  # shortcut
    WSL = bool(env.WSLENV)  # Linux Subsystem for Winders
    _color_sep = ';'  # color sequences delimiter

    if TERM.startswith('vt'):  # openbsd, hardware
        level = TermLevel.ANSI_MONOCHROME  # 525 had color

    if TERM.startswith(('xterm', 'linux')):
        level = TermLevel.ANSI_BASIC

    # upgrades
    if TERM.endswith('-256color') or is_fbterm:
        level = TermLevel.ANSI_EXTENDED

    # https://bugzilla.redhat.com/show_bug.cgi?id=1173688 - obsolete?
    if (
        env.COLORTERM in ('truecolor', '24bit')
        or WSL
        or TERM.endswith('-direct')
    ):
        level = TermLevel.ANSI_DIRECT

    if TERM.endswith('-direct'):  # need to check again
        for prefix in TERMS_DIRECT_COLON:
            if TERM.startswith(prefix):
                _color_sep = ':'; break

    _color_sep = env.PY_CONSOLE_COLOR_SEP or _color_sep  # local override
    log.debug(
        f'Terminal level: {level.name!r} ({os_name}{"-wsl" if WSL else ""}, '
        f'TERM={TERM!r}, COLORTERM={env.COLORTERM.value!r}, '
        f'TERM_PROGRAM={env.TERM_PROGRAM.value!r}, '
        f'color_sep={_color_sep!r}, source=console) '
    )
    return level, _color_sep


def detect_terminal_level_terminfo():
    ''' Use curses to query the terminfo database for the terminal support
        level

        Returns:
            level:      TermLevel member
            color_sep   The extended color sequence separator character,
                        i.e. ":" or ";".
    '''
    level = TermLevel.DUMB
    _color_sep = None
    try:
        from . import _curses

        has_underline = _curses.tigetstr('smul')
        if has_underline:   # This first test could be more granular,
                            # but it is so rare today we won't bother:
            if has_underline.startswith(bytes(CSI, 'ascii')):
                level = TermLevel.ANSI_MONOCHROME

            num_colors = _curses.tigetnum('colors')
            log.debug('tigetnum("colors") = %s', num_colors)
            # -1 means not set, leaving level unchanged from above.
            if -1 < num_colors < 50:
                level = TermLevel.ANSI_BASIC

            elif 49 < num_colors < 16777216:  # 52, 88, 256
                level = TermLevel.ANSI_EXTENDED

            elif 16777216 <= num_colors:
                level = TermLevel.ANSI_DIRECT

            if level >= TermLevel.ANSI_BASIC:
                _color_sep = ';'

            # finding color_sep is a bit problematic
            if level >= TermLevel.ANSI_EXTENDED:
                setaf = (_curses.tigetstr('setaf') or b'').decode('ascii')
                # log.debug('tigetstr setaf: %r', setaf)
                suffix = setaf.partition('38')[2]
                if suffix:
                    _color_sep = suffix[0]  # first char after 38

        _color_sep = env.PY_CONSOLE_COLOR_SEP or _color_sep  # local override
        log.debug(
          f'Terminal level: {level.name!r} ({os_name}, '
          f'TERM={env.TERM.value!r}, color_sep={_color_sep!r}, source=terminfo) '
        )
        return level, _color_sep
    except ModuleNotFoundError:
        # Fall back early when remoting to Windows w/o curses/jinxed
        # TERM variable only clue:
        log.warn('terminfo not available.')
        return detect_terminal_level()


def detect_unicode_support():
    ''' Try to detect unicode (utf8?) support in the terminal.

        Checks the ``LANG`` environment variable,
        falls back to an experimental method utilizing cursor position.
        Implementation idea is from the link below:

           https://unix.stackexchange.com/q/184345/

        Returns:
            support: Boolean | None if not a TTY
    '''
    result = None
    LANG = env.LANG.value

    if LANG and LANG.upper().endswith('UTF-8'):  # first approximation
        result = True

    elif is_a_tty():  # kludge
        stdout = sys.stdout
        x, _ = get_position()
        stdout.write('é')
        stdout.flush()
        x2, _ = get_position()

        difference = x2 - x
        if difference == 1:
            result = True
        else:
            result = False

        # clean up
        stdout.write(BS)
        stdout.flush()

    log.debug(str(result))
    return result


def _find_basic_palette_from_os():
    ''' Find the platform-dependent 16-color basic palette—posix version.

        This is used for "downgrading to the nearest color" support.
    '''
    pal_name = 'default (xterm)'
    basic_palette = DEFAULT_BASIC_PALETTE

    if env.WSLENV:  # must go first since Windows uses TERM=xterm…
        pal_name = 'cmd_1709'
        basic_palette = color_tables.cmd1709_palette4

    elif env.TERM.startswith('xterm'):
        if sys.platform.startswith('freebsd'):  # can't differentiate console
            pal_name = 'vga'
            basic_palette = color_tables.vga_palette4
        else:  # Look harder by querying terminal; get_color may timeout
            try:  # TODO: this comparison could be much better:
                colors = get_color('index', 2)
                if colors[0][:2] == '85':
                    pal_name = 'solarized'
                    basic_palette = color_tables.solarized_dark_palette4
                elif colors[0][:2] == '4e':
                    pal_name = 'tango'
                    basic_palette = color_tables.tango_palette4
                else:
                    raise RuntimeError('not a known color scheme.')
            except (IndexError, RuntimeError, termios.error) as err:
                log.debug('get_color return value failed: %s', err)

    elif env.TERM.startswith(('linux', 'fbterm')):
        pal_name = 'vtrgb'
        basic_palette = parse_vtrgb() or basic_palette

    return pal_name, basic_palette


def _find_basic_palette_from_term(term):
    ''' Find the platform-dependent 16-color basic palette—\
        remotely via TERM variable.

        This is used for "downgrading to the nearest color" support.
    '''
    from fnmatch import fnmatchcase  # case sensitive

    pal_name = 'xterm'
    basic_palette = DEFAULT_BASIC_PALETTE
    for term_spec in term_palette_map:
        if fnmatchcase(term, term_spec):  # matches
            basic_palette = term_palette_map[term_spec]
            pal_name = term_spec.rstrip('*')
            break

    return pal_name, basic_palette


def is_a_tty(stream=sys.stdout):
    ''' Detect terminal or something else, such as output redirection.

        Returns:
            Boolean, None: is tty or None if not found.
    '''
    result = stream.isatty() if hasattr(stream, 'isatty') else None
    log.debug('tty: %s', result)
    return result


def parse_vtrgb(path='/etc/vtrgb'):
    ''' Parse the color table for the Linux console.

        Returns:
            palette or None if not found.
    '''
    palette = None
    table = []
    try:
        with open(path) as infile:
            for i, line in enumerate(infile):
                row = tuple(int(val) for val in line.split(','))
                table.append(row)
                if i == 2:  # failsafe
                    break

        palette = tuple(zip(*table))  # swap rows to columns
    except IOError:
        pass

    return palette


# -- tty, termios ------------------------------------------------------------

def _get_char():
    ''' POSIX implementation of get char/key. '''
    with TermStack() as fd:
        tty.setraw(fd)
        return sys.stdin.read(1)


def _read_until_select(infile=sys.stdin, max_bytes=20, end=RS, timeout=None):
    ''' Read a terminal response of up to a given max characters from stdin,
        with timeout.  POSIX only, files not compat with select on Windows.

        Arguments:
            infile: file, stdin
            max_bytes: int, read no longer than this.
            end: str, end of data marker, one or two chars.
            timeout: float secs, how long to wait until giving up.
    '''
    from select import select
    chars = []
    read = infile.read  # shortcut
    last_char = ''
    if not isinstance(end, tuple):
        end = (end,)
    #~ log.debug('read: max_bytes=%s, end=%r, timeout %s …', max_bytes, end, timeout)

    if select((infile,), (), (), timeout)[0]:  # wait until response or timeout
        #~ log.debug('select output, start reading:')
        while max_bytes:  # response: count down chars, stopping at 0
            char = read(1)
            # print(max_bytes, repr(char))
            if char in end:  # single
                break
            if (last_char + char) in end:  # double char, i.e. ST
                del chars[-1]  # rm end[0]
                break
            chars.append(char)
            last_char = char
            max_bytes -= 1
    else:  # timeout
        log.debug('response not received in time, %s secs.', timeout)

    return ''.join(chars)


def _get_color_xterm(name, number=None, timeout=None):
    ''' Query xterm for color settings.

        Warning: likely to block on incompatible terminals, use timeout.
    '''
    colors = ()
    if name == 'index' and isinstance(number, int):
        color_code = '4;' + str(number)
    else:
        color_code = _COLOR_CODE_MAP.get(name)

    if color_code:
        query_sequence = f'{OSC}{color_code};?{ST}'
        #~ log.debug('query seq: %r', query_sequence)
        try:
            with TermStack() as fd:
                termios.tcflush(fd, termios.TCIFLUSH)   # clear input
                tty.setcbreak(fd, termios.TCSANOW)      # shut off echo
                sys.stdout.write(query_sequence)
                sys.stdout.flush()
                resp = _read_until_select(  # max bytes 26 + 2 for 256 digits
                            max_bytes=28, end=(BEL, ST), timeout=timeout
                        )
                #~ log.debug('response: %r', resp)
        except AttributeError:
            log.debug('warning - no .fileno() attribute was found on the stream.')
        except EnvironmentError:  # Winders
            log.debug('see console.windows.get_color()')
        else:  # parse response
            colors = resp.partition(':')[2].split('/')
            if colors == ['']:  # nuttin
                colors = []  # empty on failure
            colors = tuple(colors)

    return colors


def _read_clipboard(
        source='c', encoding=None, max_bytes=defaults.MAX_CLIPBOARD_SIZE,
        timeout=.2
    ):
    ''' Query xterm for clipboard data.

        Warning: likely to block on incompatible terminals, use timeout.
    '''
    resp = None
    query_sequence = f'{OSC}52;{source};?{ST}'
    try:
        with TermStack() as fd:
            termios.tcflush(fd, termios.TCIFLUSH)   # clear input
            tty.setcbreak(fd, termios.TCSANOW)      # shut off echo
            sys.stdout.write(query_sequence)
            sys.stdout.flush()
            log.debug('about to read get_color_xterm response…')
            resp = _read_until_select(  # not working on iterm, check for BEL
                        max_bytes=max_bytes, end=ST, timeout=timeout
                    )
    except AttributeError:
        log.debug('warning - no .fileno() attribute was found on the stream.')
    except EnvironmentError:  # Winders
        log.debug('_read_clipboard not yet implemented by Windows.')
    else:
        if resp:  # parse response
            from base64 import b64decode
            resp = b64decode(resp.split(';', 3)[-1])
            if encoding:
                resp = resp.decode(encoding)
    return resp


def get_answerback(max_bytes=32, end=(BEL, ST, '\n'), timeout=defaults.READ_TIMEOUT):
    ''' Returns the "answerback" string which is often empty,
        None if not available.

        Warning: Hangs unless max_bytes is a subset of the answer string *or* an
                 explicit end character(s) given, due to inability to find end.
                 https://unix.stackexchange.com/a/312991/159110
    '''
    try:
        with TermStack() as fd:
            termios.tcflush(fd, termios.TCIFLUSH)   # clear input
            tty.setcbreak(fd, termios.TCSANOW)      # shut off echo
            sys.stdout.write(ENQ)
            sys.stdout.flush()
            log.debug('about to read answerback response…')
            return _read_until_select(
                        max_bytes=max_bytes, end=end, timeout=timeout
                    )
    except AttributeError:  # 
        log.debug('warning - no .fileno() attribute was found on the stream.')
    except EnvironmentError:  # Winders
        log.debug('answerback not yet implemented by Windows.')


def get_color(name, number=None, timeout=defaults.READ_TIMEOUT):
    ''' Query the default terminal, for colors, etc.

        Direct queries supported on xterm, iTerm, perhaps others.

        Arguments:
            name: str, one of ('foreground', 'fg', 'background', 'bg',
                                or 'index')  # index grabs a palette index
            number: int, if name is index, should be an ANSI color index from
                         0…255," see links below.

        Queries terminal using ``OSC # ? BEL`` sequence,
        call responds with a color in this X Window format syntax:

            - ``rgb:DEAD/BEEF/CAFE``
            - `Control sequences
              <http://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h2-Operating-System-Commands>`_
            - `X11 colors
              <https://www.x.org/releases/X11R7.7/doc/libX11/libX11/libX11.html#RGB_Device_String_Specification>`_

        Returns:
            tuple[str]: 
                A tuple of four-digit hex strings after parsing,
                the last two digits are the least significant and can be
                chopped when needed:

                ``('DEAD', 'BEEF', 'CAFE')``

                If an error occurs during retrieval or parsing,
                the tuple will be empty.

        Examples:
            >>> get_color('bg')
            ... ('0000', '0000', '0000')

            >>> get_color('index', 2)       # second color in indexed
            ... ('4e4d', '9a9a', '0605')    # palette, 2 aka 32 in basic

        Notes:
            Query blocks until timeout if terminal does not support the function.
            Many don't.  Timeout can be disabled with None or set to a higher
            number for a slow terminal.

            On Windows, only able to find palette defaults,
            which may be different if they were customized.
    '''
    color = ()
    if sys.platform == 'darwin':  # check first
        if env.TERM_PROGRAM == 'iTerm.app':
            # supports, though returns only two chars per
            color = _get_color_xterm(name, number, timeout=timeout)

    elif os_name == 'posix':
        if env.WSLENV or env.TERM_PROGRAM == 'vscode':
            pass  # LSW, vscode on Linux don't support xterm query

        elif env.TERM =='xterm' and sys.platform.startswith('freebsd'):
            pass  # freebsd console

        elif env.TERM.startswith('xterm'):
            color = _get_color_xterm(name, number, timeout=timeout)

    # Windows impl. uses its API, Terminal has begun support of xterm query
    log.debug('%s %s color: %r', name, number, color)
    return color


def get_position(fallback=defaults.CURSOR_POS_FALLBACK):
    ''' Return the current column number of the terminal cursor.
        Used to figure out if we need to print an extra newline.

        Returns:
            tuple(int): (x, y) | (0, 0)  - fallback, if an error occurred.
    '''
    values, resp = None, ''
    try:
        with TermStack() as fd:
            termios.tcflush(fd, termios.TCIFLUSH)   # clear input
            tty.setcbreak(fd, termios.TCSANOW)      # shut off echo
            sys.stdout.write(CSI + '6n')
            sys.stdout.flush()
            log.debug('about to read get_position response…')
            resp = _read_until_select(max_bytes=10, end='R')
    except (AttributeError, OSError):  # no .fileno(), or ssh into Windows
        return fallback

    # parse response
    resp = resp.lstrip(CSI)
    try:  # reverse
        values = tuple( int(token) for token in resp.partition(';')[::-2] )
    except (ValueError, IndexError) as err:
        log.error('parse error: %s on %r', err, resp)

    return values


def get_size(fallback=defaults.TERM_SIZE_FALLBACK):
    ''' Convenience copy of `shutil.get_terminal_size
        <https://docs.python.org/3/library/shutil.html#shutil.get_terminal_size>`_
        for use here.

        ::

            >>> get_terminal_size(fallback=(80, 24))
            os.terminal_size(columns=120, lines=24)
    '''
    from shutil import get_terminal_size

    return get_terminal_size(fallback=fallback)


_query_mode_map = dict(icon=20, title=21)
def get_title(mode='title'):
    ''' Return the terminal/console title.

        Arguments:
            str:  mode,  one of ('title', 'icon') or int (20-21):
                  see links below.

        - `Control sequences
          <http://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h2-Operating-System-Commands>`_

        Returns:
            title string, or None if not able to be found.

        Note:
            Few terms besides xterm support this for security reasons.
            iTerm returns "".  MATE Terminal returns "Terminal".
    '''
    title = None
    if sys.platform == 'darwin':
        if env.TERM_PROGRAM != 'iTerm.app':
            return title

    # xterm only support
    mode = _query_mode_map.get(mode, mode)
    query_sequence = f'{CSI}{mode}t'
    try:
        with TermStack() as fd:
            termios.tcflush(fd, termios.TCIFLUSH)   # clear input
            tty.setcbreak(fd, termios.TCSANOW)      # shut off echo
            sys.stdout.write(query_sequence)
            sys.stdout.flush()
            log.debug('about to read get_title response…')
            resp = _read_until_select(max_bytes=100, end=ST, timeout=.2)
    except AttributeError:  # no .fileno()
        return title

    # parse response
    title = resp.lstrip(OSC)[1:].rstrip(ESC)

    log.debug('%r', title)
    return title


def get_theme(timeout=defaults.READ_TIMEOUT):
    ''' Checks terminal for light/dark theme information.

        First checks for the environment variable COLORFGBG.
        Next, queries terminal, supported on Windows (not WSL) and xterm,
        perhaps others.
        See notes on get_color().

        Returns:
            str, None:  'dark', 'light', or None if no information.
    '''
    theme = None
    COLORFGBG = env.COLORFGBG.value
    log.debug('COLORFGBG: %s', COLORFGBG)

    if COLORFGBG:
        FG, _, BG = COLORFGBG.partition(';')     # TODO: rxvt default;default
        theme = 'dark' if BG < '8' else 'light'  # background wins

    else:
        TERM = env.TERM.value
        if TERM =='xterm' and sys.platform.startswith('freebsd'):  # console
            theme = 'dark'
        elif TERM.startswith('xterm'):
            # try xterm query - find average across rgb
            colors = get_color('background', timeout=timeout)  # bg wins
            if colors:
                colors = tuple(int(hexclr[:2], 16) for hexclr in colors)
                avg = sum(colors) / len(colors)
                theme = 'dark' if avg < 128 else 'light'
        elif TERM.startswith(('linux', 'fbterm')):  # vga console
            theme = 'dark'
        elif TERM.startswith('vt'):  # openbsd, hardware
            theme = 'dark'

    log.debug('%r', theme)
    return theme


# Override default implementations

if os_name == 'nt' and not env.SSH_CLIENT:  # I'm a PC

    from .windows import (
        detect_unicode_support,
        detect_terminal_level,
        _find_basic_palette_from_os,
        get_color,
        get_position,
        get_title,
        get_theme,
    )

elif sys.platform == 'darwin':  # Think different

    def _find_basic_palette_from_os():
        ''' Find the platform-dependent 16-color basic palette—macOS version.

            This is used for "downgrading to the nearest color" support.
        '''
        pal_name = 'default (xterm)'
        basic_palette = DEFAULT_BASIC_PALETTE

        if env.TERM_PROGRAM == 'Apple_Terminal':
            pal_name = 'termapp'
            basic_palette = color_tables.termapp_palette4
        elif env.TERM_PROGRAM == 'iTerm.app':
            pal_name = 'iterm'
            basic_palette = color_tables.iterm_palette4

        return pal_name, basic_palette


elif os_name == 'posix':  # Tron leotards
    pass

else:  # Commodore/Amiga/Atari - The Wonder Computer of the 1980s :-D
    log.warning('Unexpected OS: os.name: %s', os_name)


if __name__ == '__main__':

    # logs the detection information sequence
    print()  # space from warnings  :-/

    try:
        #~ raise ImportError()  # testing
        import out
        out.configure(level='debug')
    except ImportError:
        fmt = '  %(levelname)-7.7s %(module)s/%(funcName)s:%(lineno)s %(message)s'
        logging.basicConfig(level=logging.DEBUG, format=fmt)

    from . import using_terminfo as _using_terminfo
    init(using_terminfo=_using_terminfo)  # run again so detection gets logged
