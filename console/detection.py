# -*- coding: future_fstrings -*-
'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    This module contains capability detection routines for use under ANSI
    compatible terminals.

    See also:

        - os & `shutil.get_terminal_size
          <https://docs.python.org/3/library/shutil.html#shutil.get_terminal_size>`_
'''
import sys, os
import logging

import env

from . import color_tables, proximity
from .constants import BEL, CSI, OSC, RS, ALL_PALETTES

log = logging.getLogger(__name__)
os_name = os.name


class TermStack:
    ''' Context Manager to save, temporarily modify, then restore terminal
        attributes.

        Arguments::
            infile      - The file object to operate on, defaulting to stdin.

        Example:
            A POSIX implementation of get char/key::

                import tty

                with TermStack() as fd:
                    tty.setraw(fd)
                    return sys.stdin.read(1)
    '''
    def __init__(self, infile=sys.stdin):
        import termios
        self.termios = termios
        self.fd = infile.fileno()

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
                                for testing.  List of 16 rgb-tuples.
        Returns:
            None, str: 'basic', 'extended', or 'truecolor'
    '''
    result = None
    if color_is_forced():
        result = detect_palette_support() or 'basic'

    elif is_a_tty(stream=stream) and color_is_allowed():
        result = detect_palette_support()

    log.debug('%r', result)

    # find the platform-dependent 16-color basic palette, set it as current:
    if result:
        if not basic_palette:
            pal_name = ''
            if os_name == 'nt':
                pal_name = 'cmd'
                basic_palette = color_tables.cmd_palette4
            elif os_name == 'darwin':
                if env.TERM_PROGRAM == 'Apple_Terminal':
                    pal_name = 'termapp'
                    basic_palette = color_tables.termapp_palette4
                elif env.TERM_PROGRAM == 'iTerm.app':
                    pal_name = 'iterm'
                    pass  # TODO: configure, defaults to vga
            elif os_name == 'posix':
                if env.TERM == 'linux':
                    pal_name = 'vtrgb'
                    basic_palette = parse_etc_vtrgb()
                elif env.TERM.startswith('xterm'):
                    pal_name = 'xterm'
                    basic_palette = color_tables.xterm_palette4
                # TODO: gnome, tango?
            else:  # Amiga/Atari :-P
                pal_name = 'unknown'
                log.warn('Unexpected OS: os.name: %s', os_name)

        proximity.build_color_tables(basic_palette)
        log.debug('os.name: %s, basic_palette: %s = %r', os_name, pal_name,
                                                         basic_palette)
    return result


def color_is_allowed():
    ''' Look for clues in environment, e.g.:

        - https://bixense.com/clicolors/
        - http://no-color.org/

        Returns:
            Bool:  Allowed
    '''
    result = True  # generally yes - env.CLICOLOR != '0'

    if color_is_disabled():
        result = False

    log.debug('%r', result)
    return result


def color_is_disabled():
    ''' Look for clues in environment, e.g.:

        - https://bixense.com/clicolors/
        - http://no-color.org/

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
    return result


def color_is_forced():
    ''' Look for clues in environment, e.g.:

        - https://bixense.com/clicolors/

        Returns:
            Bool:  Forced
    '''
    result = env.CLICOLOR_FORCE and env.CLICOLOR_FORCE != '0'
    log.debug('%s (CLICOLOR_FORCE=%s)', result, env.CLICOLOR_FORCE or '')
    return result


def detect_palette_support():
    ''' Returns whether we think the terminal supports basic, extended, or
        truecolor.  None if not able to tell.

        TODO: curses might be able to help.

        Returns:
            None or str: 'basic', 'extended', 'truecolor'
    '''
    result, col_init = None, None
    TERM = env.TERM or ''
    col_init = _is_colorama_initialized()
    try:
        import webcolors
    except ImportError:
        webcolors = None


    if ('color' in TERM) or ('linux' in TERM) or col_init:
        result = 'basic'

    if ('256color' in TERM) or env.ANSICON:  # xterm, Windows
        result = 'extended'

    # https://bugzilla.redhat.com/show_bug.cgi?id=1173688 - obsolete?
    if env.COLORTERM in ('truecolor', '24bit'):
        result = 'truecolor'

    log.debug(f'{result!r} (TERM={env.TERM or ""}, '
              f'COLORTERM={env.COLORTERM or ""}, webcolors={webcolors}, '
              f'colorama-init={col_init}')
    return result


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


def _is_colorama_initialized():
    result = None
    if os.name == 'nt':
        try:
            import colorama
            if isinstance(sys.stdout, colorama.ansitowin32.StreamWrapper):
                result = True
        except ImportError:
            pass
    return result


def parse_etc_vtrgb(path='/etc/vtrgb'):
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

        palette = tuple(zip(*table))  # swap rows to columns

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

    # count down, stopping at 0
    while maxchars:
        char = read(1)
        if char == end:
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

        with TermStack() as fd:

            tty.setcbreak(fd, termios.TCSANOW)      # shut off echo
            sys.stdout.write(CSI + '6n')            # screen.dsr, avoid import
            sys.stdout.flush()
            resp = _read_until(maxchars=10, end='R')

        # parse response
        resp = resp.lstrip(CSI)
        try:  # reverse
            values = tuple( int(token) for token in resp.partition(';')[::-2] )
        except Exception as err:
            log.error('parse error: %s on %r', err, resp)

    return values


def get_theme():
    ''' Checks system for theme information.

        First checks for the environment variable COLORFGBG.
        Next, queries terminal, supported on xterm, perhaps others.
        See notes on query_terminal_color().

        Returns:
            str, None: 'dark', 'light', None if no information.
    '''
    theme = None
    log.debug('COLORFGBG: %s', env.COLORFGBG)
    if env.COLORFGBG:
        FG, _, BG = env.COLORFGBG.partition(';')
        theme = 'dark' if BG < '8' else 'light'  # background wins
    else:
        # try xterm - find average across rgb
        colors = query_terminal_color('background')  # background wins
        if colors:
            colors = tuple(int(cm[:1], 16) for cm in colors)  # first hex char
            avg = sum(colors) / len(colors)
            theme = 'dark' if avg < 8 else 'light'

    log.debug('%r', theme)
    return theme


def query_terminal_color(name):
    ''' Query the default terminal, for colors, etc.

        Direct queries supported on xterm, perhaps others, not Windows.

        Arguments:
            str:  name,  one of ('foreground', 'fg', 'background', 'bg')
            int:  or a "dynamic color number (10-19)," see links below.

        Queries terminal using ``OSC # ? BEL`` sequence,
        call responds with a color in this X Window format syntax:

            - ``rgb:DEAD/BEEF/CAFE``
            - `Control sequences
              <http://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h2-Operating-System-Commands>`_
            - `X11 colors
              <https://www.x.org/releases/X11R7.7/doc/libX11/libX11/libX11.html#RGB_Device_String_Specification>`_

        Returns:
            list[str]: 
                A list of four-digit hex strings after parsing,
                the last two digits are the least significant and can be
                chopped if needed:

                ``['DEAD', 'BEEF', 'CAFE']``

                If an error occurs during retrieval or parsing,
                the list will be empty.

        Note:
            Checks is_a_tty() first, since function would block if i/o were
            redirected through a pipe.
    '''
    colors = []
    if is_a_tty():
        if os_name == 'nt':
            return colors
        elif os_name == 'darwin':
            if env.TERM_PROGRAM and env.TERM_PROGRAM != 'iTerm.app':
                return colors
        elif os_name == 'posix':
            if env.TERM and env.TERM.startswith('xterm'):
                pass
            else:
                return colors

        # xterm only support
        import tty, termios
        color_code = dict(foreground='10', fg='10',
                          background='11', bg='11').get(name)
        if color_code:
            query_sequence = f'{OSC}{color_code};?{BEL}'
            with TermStack() as fd:
                termios.tcflush(fd, termios.TCIFLUSH)   # needed by xterm osx

                tty.setcbreak(fd, termios.TCSANOW)      # shut off echo
                sys.stdout.write(query_sequence)
                sys.stdout.flush()
                resp = _read_until(maxchars=24, end=BEL)

            # parse response
            colors = resp.partition(':')[2].split('/')
            if colors == ['']:
                colors = []                             # empty on failure

    return colors
