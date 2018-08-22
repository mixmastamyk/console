'''
    | console - Comprehensive escape sequence utility library for terminals.
    | © 2018, Mike Miller - Released under the LGPL, version 3+.

    This module contains capability detection routines for use under ANSI
    compatible terminals.

    See also:

        - os & shutil.get_terminal_size
'''
import sys
import logging

import env

from .constants import BEL, CSI, OSC, RS


log = logging.getLogger(__name__)


class TermStack:
    ''' Context Manager to save, temporarily modify, then restore terminal
        attributes.
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


def choose_palette(force_to='basic'):
    ''' Make a best effort to automatically determine whether to enable
        ANSI color sequences, and if so, which palette to use.

        This is the main function of the module—meant to be used unless
        something more specific is needed.

        Takes the following factors into account:

        - Whether output stream is a TTY.
        - TERM, ANSICON environment variables
        - CLICOLOR, NO_COLOR environment variables

        Returns:
            None, 'basic', 'extended', or 'true'
    '''
    result = None

    if color_is_forced():
        result = detect_palette_support() or force_to

    elif is_a_tty() and color_is_allowed():
        result = detect_palette_support()

    log.debug('%r', result)
    return result


def color_is_allowed():
    ''' Look for clues, e.g.:

        - https://bixense.com/clicolors/
        - http://no-color.org/
    '''
    result = True  # generally yes - env.CLICOLOR != '0'

    if color_is_disabled():
        result = False

    log.debug('%r', result)
    return result


def color_is_disabled():
    ''' Look for clues, e.g.:

        - https://bixense.com/clicolors/
        - http://no-color.org/
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
    ''' Look for clues, e.g.:
            - https://bixense.com/clicolors/
    '''
    result = env.CLICOLOR_FORCE and env.CLICOLOR_FORCE != '0'
    log.debug('%s (CLICOLOR_FORCE=%s)', result, env.CLICOLOR_FORCE or '')
    return result


def detect_palette_support():
    ''' Returns whether we think the terminal supports basic, extended, or
        truecolor.  None if not able to tell.

        TODO: needs work - could we use terminfo or curses for this?
    '''
    result = None
    TERM = env.TERM or ''

    if ('color' in TERM) or ('linux' in TERM):
        result = 'basic'

    if ('256color' in TERM) or env.ANSICON:  # xterm, Windows
        result = 'extended'

    # https://bugzilla.redhat.com/show_bug.cgi?id=1173688 - obsolete?
    if env.COLORTERM in ('truecolor', '24bit'):
        result = 'truecolor'

    log.debug('%r (TERM=%s, COLORTERM=%s)', result, env.TERM or '',
                                            env.COLORTERM or '')
    return result


def is_a_tty(outfile=sys.stdout):
    ''' Detect terminal or something else, such as output redirection.

        Returns: Boolean or None if not found.
    '''
    result = outfile.isatty() if hasattr(outfile, 'isatty') else None
    log.debug(result)
    return result


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
            (x, y) - as tuple of integers
            (,)    - empty tuple, if an error occurred.

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
    ''' Supported on xterm, perhaps others.

        See notes on query_terminal_color().
    '''
    theme = 'dark'
    for component in query_terminal_color('background'):
        if component and component[0] > '7':
            theme = 'light'
            break
    return theme


def query_terminal_color(name):
    ''' Query the default terminal, for colors, etc.
        Supported on xterm, perhaps others, not Windows.
        TODO: check xterm env variable.

        Arguments:
            name - str - one of ('foreground', 'fg', 'background', 'bg')
                         or a "dynamic color number (10-19)," see link below.

        Queries terminal using OSC # ? BEL sequence documented below:
            http://invisible-island.net/xterm/ctlseqs/ctlseqs.html⏎
                #h2-Operating-System-Commands

        Call responds with a color in this X Window format syntax:
            rgb:DEAD/BEEF/CAFE

            https://www.x.org/releases/X11R7.7/doc/libX11/libX11/libX11.html
                #RGB_Device_String_Specification

        Returns:
            A list of four-digit hex strings after parsing,
            the fourth digit is the least significant and can be chopped if
            needed:

            ``['DEAD', 'BEEF', 'CAFE']``

            If an error occurs during retrieval or parsing,
            the list will be empty.

        Note:
            Checks is_a_tty() first, since function would block if i/o were
            redirected through a pipe.
    '''
    import tty, termios

    colors = []
    if is_a_tty():
        color_code = dict(foreground='10', fg='10',
                          background='11', bg='11').get(name)
        if color_code:
            query_sequence = f'{OSC}{color_code};?{BEL}'
            with TermStack() as fd:

                tty.setcbreak(fd, termios.TCSANOW)      # shut off echo
                sys.stdout.write(query_sequence)
                sys.stdout.flush()
                resp = _read_until(maxchars=24, end=BEL)

            # parse response
            colors = resp.partition(':')[2].split('/')
            if colors == ['']:
                colors = []                             # empty on failure

    return colors
