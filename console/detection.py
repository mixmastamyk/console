# -*- coding: future_fstrings -*-
'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    This module contains capability detection routines for use under ANSI
    compatible terminals.
'''
import sys, os
import logging

import env

from . import color_tables, proximity, __version__
from .constants import BEL, CSI, ESC, OSC, RS, ST, ALL_PALETTES

log = logging.getLogger(__name__)
os_name = os.name
TERM_SIZE_FALLBACK = (80, 24)

# X11 colors support
X11_RGB_PATHS = ()  # Windows
if sys.platform == 'darwin':
    X11_RGB_PATHS = ('/opt/X11/share/X11/rgb.txt',)
elif os.name == 'posix':  # Ubuntu, FreeBSD
    X11_RGB_PATHS = ('/etc/X11/rgb.txt', '/usr/share/X11/rgb.txt',
                     '/usr/local/lib/X11/rgb.txt', '/usr/X11R6/lib/X11/rgb.txt')


class TermStack:
    ''' Context Manager to save, temporarily modify, then restore terminal
        attributes.

        Arguments::
            stream      - The file object to operate on, defaulting to stdin.

        Raises:
            AttributeError: when stream has no attribute 'fileno'

        Example:
            A POSIX implementation of get char/key::

                import tty

                with TermStack() as fd:
                    tty.setraw(fd)
                    return sys.stdin.read(1)
    '''
    def __init__(self, stream=sys.stdin):
        import termios
        self.termios = termios
        self.fd = stream.fileno()

    def __enter__(self):
        # save
        self.orig_attrs = self.termios.tcgetattr(self.fd)
        return self.fd

    def __exit__(self, *args):
        # restore
        self.termios.tcsetattr(self.fd, self.termios.TCSADRAIN,
                               self.orig_attrs)


def choose_palette(stream=sys.stdout, basic_palette=None):
    ''' Make a best effort to automatically determine whether to enable
        ANSI sequences, and if so, which color palettes are available.

        This is the main function of the module—meant to be used unless
        something more specific is needed.

        Takes the following factors into account:

        - Whether output stream is a TTY.
        - ``TERM``, ``ANSICON`` environment variables
        - ``CLICOLOR``, ``NO_COLOR`` environment variables

        Arguments:
            stream:             Which output file to check: stdout, stderr
            basic_palette:      Force the platform-dependent 16 color palette,
                                for testing.  List of 16 rgb-int tuples.
        Returns:
            None, str: 'basic', 'extended', or 'truecolor'
    '''
    result = None
    pal = basic_palette
    log.debug('version: %r', __version__)
    log.debug('X11_RGB_PATHS: %r', X11_RGB_PATHS)

    if color_is_forced():
        result, pal = detect_palette_support(basic_palette=pal) or 'basic'

    elif is_a_tty(stream=stream) and color_is_allowed():
        result, pal = detect_palette_support(basic_palette=pal)

    proximity.build_color_tables(pal)
    log.debug('Basic palette: %r', pal)
    log.debug('%r', result)
    return result


def color_is_allowed():
    ''' Look for clues in environment, e.g.:

        - https://bixense.com/clicolors/
        - http://no-color.org/

        Returns:
            Bool:  Allowed
    '''
    result = True  # generally yes - env.CLICOLOR != '0'

    if color_is_disabled():
        result = False

    log.debug('%r', result)
    return result


def color_is_disabled(**envars):
    ''' Look for clues in environment, e.g.:

        - https://bixense.com/clicolors/
        - http://no-color.org/

        Arguments:
            envars:     Additional environment variables to check for
                        equality, i.e. ``MYAPP_COLOR_DISABLED='1'``

        Returns:
            None, Bool:  Disabled
    '''
    result = None
    if 'NO_COLOR' in env:
        result = True
    elif env.CLICOLOR == '0':
        result = True

    log.debug('%r (NO_COLOR=%s, CLICOLOR=%s)', result,
              env.NO_COLOR or '',
              env.CLICOLOR or ''
    )
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
            envars:     Additional environment variables to check for
                        equality, i.e. ``MYAPP_COLOR_FORCED='1'``
        Returns:
            Bool:  Forced
    '''
    result = env.CLICOLOR_FORCE and env.CLICOLOR_FORCE != '0'
    log.debug('%s (CLICOLOR_FORCE=%s)', result, env.CLICOLOR_FORCE or '')

    for name, value in envars.items():
        envar = getattr(env, name)
        if envar.value == value:
            result = True
        log.debug('%s == %r: %r', name, value, result)

    return result


def detect_palette_support(basic_palette=None):
    ''' Returns whether we think the terminal supports basic, extended, or
        truecolor.  None if not able to tell.

        Returns:
            None or str: 'basic', 'extended', 'truecolor'
    '''
    result = col_init = win_enabled = None
    TERM = env.TERM or ''
    if os_name == 'nt':
        from .windows import (is_ansi_capable, enable_vt_processing,
                              is_colorama_initialized)
        if is_ansi_capable():
            win_enabled = all(enable_vt_processing())
        col_init = is_colorama_initialized()

    try:
        import webcolors
    except ImportError:
        webcolors = None

    # linux, older Windows + colorama
    if ('color' in TERM) or (TERM == 'linux') or col_init:
        result = 'basic'

    # xterm, fbterm, older Windows + ansicon
    if ('256color' in TERM) or (TERM == 'fbterm') or env.ANSICON:
        result = 'extended'

    # https://bugzilla.redhat.com/show_bug.cgi?id=1173688 - obsolete?
    if env.COLORTERM in ('truecolor', '24bit') or win_enabled:
        result = 'truecolor'

    # find the platform-dependent 16-color basic palette
    pal_name = 'Unknown'
    if result and not basic_palette:
        result, pal_name, basic_palette = _find_basic_palette(result)

    log.debug(
        f'{result!r} ({os_name}, TERM={env.TERM or ""}, '
        f'COLORTERM={env.COLORTERM or ""}, ANSICON={env.ANSICON}, '
        f'webcolors={bool(webcolors)}, basic_palette={pal_name})'
    )
    return (result, basic_palette)


def _find_basic_palette(result):
    ''' Find the platform-dependent 16-color basic palette.

        This is used for "downgrading to the nearest color" support.
    '''
    if env.SSH_CLIENT:  # fall back to xterm over ssh, info often wrong
        pal_name = 'ssh (xterm)'
        basic_palette = color_tables.xterm_palette4
    else:
        if os_name == 'nt':
            if sys.getwindowsversion()[2] > 16299: # Win10 FCU, new palette
                pal_name = 'cmd_1709'
                basic_palette = color_tables.cmd1709_palette4
            else:
                pal_name = 'cmd_legacy'
                basic_palette = color_tables.cmd_palette4
        elif sys.platform == 'darwin':
            if env.TERM_PROGRAM == 'Apple_Terminal':
                pal_name = 'termapp'
                basic_palette = color_tables.termapp_palette4
            elif env.TERM_PROGRAM == 'iTerm.app':
                pal_name = 'iterm'
                basic_palette = color_tables.iterm_palette4
        elif os_name == 'posix':
            if env.TERM in ('linux', 'fbterm'):
                pal_name = 'vtrgb'
                basic_palette = parse_vtrgb()
            elif env.TERM.startswith('xterm'):
                # fix: LOW64 - Python on Linux on Windows!
                if 'Microsoft' in os.uname().release:
                    pal_name = 'cmd_1709'
                    basic_palette = color_tables.cmd1709_palette4
                    result = 'truecolor'
                else:
                    try:  # TODO: check green to identify palette, others?
                        if get_color('index', 2)[0][:2] == '4e':
                            pal_name = 'tango'
                            basic_palette = color_tables.tango_palette4
                        else:
                            raise RuntimeError('not the color scheme.')
                    except (IndexError, RuntimeError):
                        pal_name = 'xterm'
                        basic_palette = color_tables.xterm_palette4
        else:  # Amiga/Atari :-P
            log.warn('Unexpected OS: os.name: %s', os_name)

    return result, pal_name, basic_palette


def get_available_palettes(chosen_palette):
    ''' Given a chosen palette, returns tuple of those available,
        or None when not found.

        Because palette support of a particular level is almost always a
        superset of lower levels, this should return all available palettes.

        Returns:
            Boolean, None: is tty or None if not found.
    '''
    result = None
    try:
        result = ALL_PALETTES[:ALL_PALETTES.index(chosen_palette)+1]
    except ValueError:
        pass
    return result


def is_a_tty(stream=sys.stdout):
    ''' Detect terminal or something else, such as output redirection.

        Returns:
            Boolean, None: is tty or None if not found.
    '''
    result = stream.isatty() if hasattr(stream, 'isatty') else None
    log.debug(result)
    return result


def load_x11_color_map(paths=X11_RGB_PATHS):
    ''' Load and parse X11's rgb.txt.

        Loads:
            x11_color_map: { name_lower: ('R', 'G', 'B') }
    '''
    if type(paths) is str:
        paths = (paths,)

    x11_color_map = color_tables.x11_color_map
    for path in paths:
        try:
            with open(path) as infile:
                for line in infile:
                    if line.startswith('!') or line.isspace():
                        continue

                    tokens = line.rstrip().split(maxsplit=3)
                    key = tokens[3]
                    if ' ' in key:  # skip names with spaces to match webcolors
                        continue

                    x11_color_map[key.lower()] = tuple(tokens[:3])
            log.debug('X11 palette found at %r.', path)
            break
        except FileNotFoundError as err:
            log.debug('X11 palette file not found: %r', path)
        except IOError as err:
            log.debug('X11 palette file not read: %s', err)


def parse_vtrgb(path='/etc/vtrgb'):
    ''' Parse the color table for the Linux console. '''
    palette = ()
    table = []
    try:
        with open(path) as infile:
            for i, line in enumerate(infile):
                row = tuple(int(val) for val in line.split(','))
                table.append(row)
                if i == 2:  # failsafe
                    break

        palette = tuple(zip(*table))  # swap rows to columns

    except IOError as err:
        palette = color_tables.vga_palette4

    return palette


# -- tty, termios ------------------------------------------------------------

def _getch():
    ''' POSIX implementation of get char/key. '''
    import tty

    with TermStack() as fd:
        tty.setraw(fd)
        return sys.stdin.read(1)


def _read_until(infile=sys.stdin, maxchars=20, end=RS):
    ''' Read a terminal response of up to a few characters from stdin.  '''
    chars = []
    read = infile.read
    if not isinstance(end, tuple):
        end = (end,)

    # count down, stopping at 0
    while maxchars:
        char = read(1)
        if char in end:
            break
        chars.append(char)
        maxchars -= 1

    return ''.join(chars)


def get_cursor_pos():
    ''' Return the current column number of the terminal cursor.
        Used to figure out if we need to print an extra newline.

        Returns:
            tuple(int): (x, y), (,)  - empty, if an error occurred.

        Note:
            Checks is_a_tty() first, since function would block if i/o were
            redirected through a pipe.
    '''
    values = ()
    if is_a_tty():
        import tty, termios
        try:
            with TermStack() as fd:
                tty.setcbreak(fd, termios.TCSANOW)      # shut off echo
                sys.stdout.write(CSI + '6n')            # screen.dsr, avoid import
                sys.stdout.flush()
                resp = _read_until(maxchars=10, end='R')
        except AttributeError:  # no .fileno()
            return values

        # parse response
        resp = resp.lstrip(CSI)
        try:  # reverse
            values = tuple( int(token) for token in resp.partition(';')[::-2] )
        except Exception as err:
            log.error('parse error: %s on %r', err, resp)

    return values


_color_code_map = dict(foreground='10', fg='10', background='11', bg='11')
def get_color(name, number=None):
    ''' Query the default terminal, for colors, etc.

        Direct queries supported on xterm, iTerm, perhaps others.

        Arguments:
            str:  name,  one of ('foreground', 'fg', 'background', 'bg',
                                 or 'index')  # index grabs a palette index
            int:  or a "dynamic color number of (4, 10-19)," see links below.
            str:  number - if name is index, number should be an int from 0…255

        Queries terminal using ``OSC # ? BEL`` sequence,
        call responds with a color in this X Window format syntax:

            - ``rgb:DEAD/BEEF/CAFE``
            - `Control sequences
              <http://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h2-Operating-System-Commands>`_
            - `X11 colors
              <https://www.x.org/releases/X11R7.7/doc/libX11/libX11/libX11.html#RGB_Device_String_Specification>`_

        Returns:
            tuple[int]: 
                A tuple of four-digit hex strings after parsing,
                the last two digits are the least significant and can be
                chopped if needed:

                ``('DEAD', 'BEEF', 'CAFE')``

                If an error occurs during retrieval or parsing,
                the tuple will be empty.

        Examples:
            >>> get_color('bg')
            ('0000', '0000', '0000')

            >>> get_color('index', 2)   # second color in indexed
            ('4e4d', '9a9a', '0605')    # palette, 2 aka 32 in basic

        Note:
            Blocks if terminal does not support the function.
            Checks is_a_tty() first, since function would also block if i/o
            were redirected through a pipe.

            On Windows, only able to find palette defaults,
            which may be different if they were customized.
            To find the palette index instead,
            see ``windows.get_console_color``.
    '''
    colors = ()
    if is_a_tty() and not env.SSH_CLIENT:
        if not 'index' in _color_code_map:
            _color_code_map['index'] = '4;' + str(number or '')

        if os.name == 'nt':
            from .windows import get_console_color
            color_id = get_console_color(name)
            if sys.getwindowsversion()[2] > 16299:  # Win10 FCU, new palette
                basic_palette = color_tables.cmd1709_palette4
            else:
                basic_palette = color_tables.cmd_palette4
            colors = (f'{i:02x}' for i in basic_palette[color_id]) # compat

        elif sys.platform == 'darwin':
            if env.TERM_PROGRAM and env.TERM_PROGRAM == 'iTerm.app':
                pass  # supports, though returns two chars per

        elif os.name == 'posix':
            if env.TERM and env.TERM.startswith('xterm'):
                import tty, termios
                color_code = _color_code_map.get(name)
                if color_code:
                    query_sequence = f'{OSC}{color_code};?{BEL}'
                    try:
                        with TermStack() as fd:
                            termios.tcflush(fd, termios.TCIFLUSH)  # clear input
                            tty.setcbreak(fd, termios.TCSANOW)  # shut off echo
                            sys.stdout.write(query_sequence)
                            sys.stdout.flush()
                            resp = _read_until(maxchars=26, end=(BEL, ST)).rstrip(ESC)
                    except AttributeError:  # no .fileno()
                        return colors
                    else:  # parse response
                        colors = resp.partition(':')[2].split('/')
                        if colors == ['']:
                            colors = []  # empty on failure
    return tuple(colors)


def get_size(fallback=TERM_SIZE_FALLBACK):
    ''' Convenience copy of `shutil.get_terminal_size
        <https://docs.python.org/3/library/shutil.html#shutil.get_terminal_size>`_.

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
            Experimental, few terms outside xterm support this correctly.
            MATE Terminal returns "Terminal".
            iTerm returns "".
    '''
    title = None
    if is_a_tty() and not env.SSH_CLIENT:
        if os.name == 'nt':
            from .windows import get_console_title
            return get_console_title()

        elif sys.platform == 'darwin':
            if env.TERM_PROGRAM and env.TERM_PROGRAM == 'iTerm.app':
                pass
            else:
                return
        elif os.name == 'posix':
            pass

        # xterm (maybe iterm) only support
        import tty, termios

        mode = _query_mode_map.get(mode, mode)
        query_sequence = f'{CSI}{mode}t'
        try:
            with TermStack() as fd:
                termios.tcflush(fd, termios.TCIFLUSH)   # clear input

                tty.setcbreak(fd, termios.TCSANOW)      # shut off echo
                sys.stdout.write(query_sequence)
                sys.stdout.flush()
                resp = _read_until(maxchars=100, end=ST)
        except AttributeError:  # no .fileno()
            return title

        # parse response
        title = resp.lstrip(OSC)[1:].rstrip(ESC)

    log.debug('%r', title)
    return title


def get_theme():
    ''' Checks system for theme information.

        First checks for the environment variable COLORFGBG.
        Next, queries terminal, supported on Windows and xterm, perhaps others.
        See notes on get_color().

        Returns:
            str, None: 'dark', 'light', None if no information.
    '''
    theme = None
    log.debug('COLORFGBG: %s', env.COLORFGBG)
    if env.COLORFGBG:
        FG, _, BG = env.COLORFGBG.partition(';')
        theme = 'dark' if BG < '8' else 'light'  # background wins
    else:
        if os.name == 'nt':
            from .windows import get_console_color
            color_id = get_console_color('background')
            theme = 'dark' if color_id < 8 else 'light'
        elif os.name == 'posix':
            if env.TERM in ('linux', 'fbterm'):  # default
                theme = 'dark'
            else:
                # try xterm - find average across rgb
                colors = get_color('background')  # bg wins
                if colors:
                    colors = tuple(int(cm, 16) for cm in colors)
                    avg = sum(colors) / len(colors)
                    theme = 'dark' if avg < 128 else 'light'

    log.debug('%r', theme)
    return theme
