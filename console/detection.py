# -*- coding: future_fstrings -*-
'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    This module contains capability detection routines for use under ANSI
    compatible terminals.  Most functions return None when not able to detect
    requested information.

    TODO: not entirely sure what to do over ssh, currently downgrades
          capabilities somewhat.
'''
import sys, os
import logging

import env

from . import color_tables, proximity
from .constants import (BS, BEL, CSI, ESC, ENQ, OSC, RS, ST, ALL_PALETTES,
                        _color_code_map)
from .meta import __version__, defaults


log = logging.getLogger(__name__)
os_name = os.name  # frequent use
is_fbterm = termios = tty = None


if os_name == 'posix':  # Tron leotards
    import termios, tty
    is_fbterm = (env.TERM == 'fbterm')


class TermStack:
    ''' Context Manager to save, temporarily modify, then restore terminal
        attributes.  Unix-like only.

        Arguments::
            stream      - The file object to operate on, defaulting to stdin.

        Raises:
            AttributeError: when stream has no attribute 'fileno'

        Example:
            A POSIX implementation of get char/key::

                import tty

                with TermStack() as fd:
                    tty.setraw(fd)
                    print(sys.stdin.read(1))
    '''
    def __init__(self, stream=sys.stdin):
        if not termios:
            raise EnvironmentError('The termios module was not loaded, is '
                                   'this a POSIX environment?')
        self.fd = stream.fileno()

    def __enter__(self):
        # save
        self.orig_attrs = termios.tcgetattr(self.fd)
        return self.fd

    def __exit__(self, *args):
        # restore
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.orig_attrs)


def choose_palette(stream=sys.stdout, basic_palette=None):
    ''' Make a best effort to automatically determine whether to enable ANSI
        sequences, and if so, which color palettes are available.

        This is the main function of the module—meant to be used unless
        something more specific is needed.

        Takes the following factors into account:

        - Whether output stream is a TTY.
        - ``TERM``, ``ANSICON`` environment variables, among others.
        - ``CLICOLOR``, ``CLICOLOR_FORCE``, NO_COLOR`` environment variables

        Arguments:
            stream:             Which output file to check: stdout, stderr
            basic_palette:      Force the platform-dependent 16 color palette,
                                for testing.  Tuple of 16 rgb-int tuples.
        Returns:
            None | str: 'basic', 'extended', or 'truecolor'
    '''
    result = None
    pal = basic_palette
    log.debug('console version: %s', __version__)
    log.debug('os.name/sys.platform: %s/%s', os_name, sys.platform)

    if color_is_forced() or (not color_is_disabled() and is_a_tty(stream=stream)):
        # detecten Sie, bitte
        result, pal = detect_palette_support(basic_palette=pal)
        proximity.build_color_tables(pal)

    log.debug('Basic palette: %r', pal)
    log.debug('%r is available', result)
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
    elif env.CLICOLOR:
        result = False

    log.debug('%r (NO_COLOR=%s, CLICOLOR=%s)',
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
            Bool:  Forced
    '''
    result = env.CLICOLOR_FORCE and (env.CLICOLOR_FORCE != '0')
    log.debug('%s (CLICOLOR_FORCE=%s)', result or None, env.CLICOLOR_FORCE or None)

    # check custom variables
    for name, value in envars.items():
        envar = getattr(env, name)
        if envar.value == value:
            result = True
        log.debug('%s == %r: %r', name, value, result)

    return result


def detect_palette_support(basic_palette=None):
    ''' Returns whether we think the terminal supports basic, extended, or
        truecolor; None if not able to tell.

        Arguments:
            basic_palette   A custom 16 color palette.
                            If not given, an an attempt to detect the platform
                            standard is made.
        Returns:
            Tuple of:
                name:       None or str: 'basic', 'extended', 'truecolor'
                palette:    16 * 3 tuple of colors
    '''
    name = webcolors = None
    TERM = env.TERM or ''  # shortcut
    pal_name = 'Unknown'

    if TERM.startswith('xterm') or (TERM == 'linux'):
        name = 'basic'

    # upgrades
    if ('256color' in TERM) or is_fbterm:
        name = 'extended'

    # https://bugzilla.redhat.com/show_bug.cgi?id=1173688 - obsolete?
    if env.COLORTERM in ('truecolor', '24bit'):
        name = 'truecolor'

    # find the platform-dependent 16-color basic palette
    if name and not basic_palette:
        name, pal_name, basic_palette = _find_basic_palette(name)

    if name == 'truecolor':
        try:
            import webcolors
        except ImportError:
            pass

    log.debug(
        f'Term support: {name!r} ({os_name}, TERM={env.TERM}, '
        f'COLORTERM={env.COLORTERM or ""}, '
        f'webcolors={bool(webcolors)}, basic_palette={pal_name})'
    )
    return (name, basic_palette)


def detect_unicode_support():
    ''' Try to detect unicode (utf8?) support in the terminal.

        Checks the ``LANG`` environment variable or Windows code page,
        falls back to an experimental method.
        Implementation idea is from the link below:

           https://unix.stackexchange.com/q/184345/

        Returns:
            Boolean | None if not a TTY
    '''
    result = None

    if env.LANG and env.LANG.endswith('UTF-8'):  # first approximation
        result = True

    elif is_a_tty():  # kludge

        out = sys.stdout
        x, _ = get_position()
        out.write('é')
        out.flush()
        x2, _ = get_position()

        difference = x2 - x
        if difference == 1:
            result = True
        else:
            result = False

        # clean up
        out.write(BS)
        out.flush()

    log.debug(str(result))
    return result


def _find_basic_palette(name):
    ''' Find the platform-dependent 16-color basic palette—posix version.

        This is used for "downgrading to the nearest color" support.

        Arguments:
            name        This is passed on the possibility it may need to be
                        overridden, due to WSL oddities.
    '''
    pal_name = 'default (xterm)'
    basic_palette = color_tables.xterm_palette4

    if env.SSH_CLIENT:  # fall back to xterm over ssh, info often wrong
        pal_name = 'ssh (xterm)'
    else:
        if env.TERM in ('linux', 'fbterm'):
            pal_name = 'vtrgb'
            basic_palette = parse_vtrgb()

        elif env.TERM.startswith('xterm'):   # TODO: factor, get_theme
            # LOW64 - Python on Linux on Windows!
            if 'WSLENV' in env: # or ('Microsoft' in os.uname().release):
                pal_name = 'cmd_1709'
                basic_palette = color_tables.cmd1709_palette4
                name = 'truecolor'  # override
            elif sys.platform.startswith('freebsd'):
                pal_name = 'vga'  # TODO: is valid?  vga console
                basic_palette = color_tables.vga_palette4

            # Look harder by querying terminal.
            # This can be dangerous, as get_color could potentially hang:
            else:
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

    return name, pal_name, basic_palette


def get_available_palettes(chosen_palette):
    ''' Given a chosen palette, returns tuple of those available,
        or None when not found.

        Because palette support of a particular level is almost always a
        superset of lower levels, this should return all available palettes.

        Returns:
            Boolean | None: is tty or None if not found.
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

    except IOError:
        palette = color_tables.vga_palette4

    return palette


# -- tty, termios ------------------------------------------------------------

def _get_char():
    ''' POSIX implementation of get char/key. '''
    with TermStack() as fd:
        tty.setraw(fd)
        return sys.stdin.read(1)


def _read_until_select(infile=sys.stdin, maxbytes=20, end=RS, timeout=None):
    ''' Read a terminal response of up to a given max characters from stdin,
        with timeout.  POSIX only, files not compat with select on Windows.
    '''
    from select import select
    chars = []
    read = infile.read
    if not isinstance(end, tuple):
        end = tuple(end)
    log.debug('maxbytes=%s, end=%r, timeout %s …', maxbytes, end, timeout)

    if select((infile,), (), (), timeout)[0]:  # wait until response or timeout
        log.debug('select start reading:')
        while maxbytes:  # response: count down chars, stopping at 0
            char = read(1)
            if char in end:  # simple search, doesn't consider sequence
                break
            chars.append(char)
            maxbytes -= 1
    else:  # timeout
        log.debug('response not received in time, %s secs.', timeout)

    return ''.join(chars)


def _get_color_xterm(name, number=None, timeout=None):
    ''' Query xterm for color settings.

        Warning: likely to block on incompatible terminals, use timeout.
    '''
    colors = ()
    color_code = _color_code_map.get(name)
    if color_code:
        query_sequence = f'{OSC}{color_code};?{BEL}'
        try:
            with TermStack() as fd:
                termios.tcflush(fd, termios.TCIFLUSH)   # clear input
                tty.setcbreak(fd, termios.TCSANOW)      # shut off echo
                sys.stdout.write(query_sequence)
                sys.stdout.flush()
                log.debug('about to read get_color_xterm response…')
                resp = _read_until_select(
                            maxbytes=26, end=(BEL, ST), timeout=timeout
                        ).rstrip(ESC)
        except AttributeError:
            log.debug('warning - no .fileno() attribute was found on the stream.')
        except EnvironmentError:  # Winders
            log.debug('get_color not yet implemented by Windows.')
        else:  # parse response
            colors = resp.partition(':')[2].split('/')
            if colors == ['']:  # nuttin
                colors = []  # empty on failure

    return colors


def get_answerback(maxbytes=32, end=(), timeout=defaults.READ_TIMEOUT):
    ''' Returns the "answerback" string which is often empty,
        None if not available.

        Warning: Hangs unless maxbytes is a subset of the answer string *or* an
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
                        maxbytes=maxbytes, end=end, timeout=timeout
                    )
    except AttributeError:  # 
        log.debug('warning - no .fileno() attribute was found on the stream.')
    except EnvironmentError:  # Winders
        log.debug('answerback not yet implemented by Windows.')


def get_color(name, number=None, timeout=defaults.READ_TIMEOUT):
    ''' Query the default terminal, for colors, etc.

        Direct queries supported on xterm, iTerm, perhaps others.

        Arguments:
            str:  name, one of ('foreground', 'fg', 'background', 'bg',
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
            Checks is_a_tty() first, since function would also block if i/o
            were redirected through a pipe.

            Query blocks until timeout if terminal does not support the function.
            Many don't.  Timeout can be disabled with None or set to a higher
            number for a slow terminal.

            On Windows, only able to find palette defaults,
            which may be different if they were customized.
            To find the palette index instead,
            see ``windows.get_color``.
    '''
    colors = ()
    if is_a_tty():
        if not 'index' in _color_code_map:
            _color_code_map['index'] = '4;' + str(number or '')

        if sys.platform == 'darwin':
            if env.TERM_PROGRAM == 'iTerm.app':
                # supports, though returns two chars per
                colors = _get_color_xterm(name, number, timeout=timeout)

        elif os_name == 'posix':
            if sys.platform.startswith('freebsd'):  # TODO, may not be console
                pass
            elif env.TERM:
                if env.TERM.startswith('xterm'):
                    if env.TERM_PROGRAM == 'vscode':  # vscode on Linux hangs
                        pass
                    else:
                        colors = _get_color_xterm(name, number, timeout=timeout)

    return tuple(colors)


def get_position(fallback=defaults.CURSOR_POS_FALLBACK):
    ''' Return the current column number of the terminal cursor.
        Used to figure out if we need to print an extra newline.

        Returns:
            tuple(int): (x, y), (,)  - empty, if an error occurred.

        Note:
            Checks is_a_tty() first, since function would block if i/o were
            redirected through a pipe.
    '''
    values = fallback
    if is_a_tty():
        try:
            with TermStack() as fd:
                tty.setcbreak(fd, termios.TCSANOW)      # shut off echo
                sys.stdout.write(CSI + '6n')            # screen.dsr, avoid import
                sys.stdout.flush()
                log.debug('about to read get_position response…')
                resp = _read_until_select(maxbytes=10, end='R')
        except AttributeError:  # no .fileno()
            return values

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
            Few terms besides xterm support this, for security reasons.
            iTerm returns "".  MATE Terminal returns "Terminal".
    '''
    title = None
    if is_a_tty(): # and not env.SSH_CLIENT:
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
                resp = _read_until_select(maxbytes=100, end=ST, timeout=.2)
        except AttributeError:  # no .fileno()
            return title

        # parse response
        title = resp.lstrip(OSC)[1:].rstrip(ESC)

    log.debug('%r', title)
    return title


def get_theme(timeout=defaults.READ_TIMEOUT):
    ''' Checks terminal for light/dark theme information.

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

    else:  # TODO: factor, same as _find_basic_pal
        if env.TERM in ('linux', 'fbterm'):  # default
            theme = 'dark'
        elif sys.platform.startswith('freebsd'):  # vga console :-/
            theme = 'dark'
        elif env.TERM.startswith('xterm'):
            # LOW64 - Python on Linux on Windows!
            if 'WSLENV' in env: # or ('Microsoft' in os.uname().release):
                pass  # don't know for sure.
            else:
                # try xterm query - find average across rgb
                colors = get_color('background', timeout=timeout)  # bg wins
                if colors:
                    colors = tuple(int(hexclr[:2], 16) for hexclr in colors)
                    avg = sum(colors) / len(colors)
                    theme = 'dark' if avg < 128 else 'light'

    log.debug('%r', theme)
    return theme


# Override default implementations

if os_name == 'nt':  # I'm a PC

    from .windows import (
        detect_unicode_support,
        detect_palette_support,
        _find_basic_palette,
        get_color,
        get_position,
        get_title,
        get_theme,
    )

elif sys.platform == 'darwin':  # Think different

    def _find_basic_palette_macos(name):
        ''' Find the platform-dependent 16-color basic palette—macOS version.

            This is used for "downgrading to the nearest color" support.

            Arguments:
                name        This is passed on the possibility it may need to be
                            overridden, due to WSL oddities.
        '''
        pal_name = 'default (xterm)'
        basic_palette = color_tables.xterm_palette4

        if env.SSH_CLIENT:  # fall back to xterm over ssh, info often wrong
            pal_name = 'ssh (xterm)'
        else:
            if env.TERM_PROGRAM == 'Apple_Terminal':
                pal_name = 'termapp'
                basic_palette = color_tables.termapp_palette4
            elif env.TERM_PROGRAM == 'iTerm.app':
                pal_name = 'iterm'
                basic_palette = color_tables.iterm_palette4

        return name, pal_name, basic_palette


elif os_name == 'posix':  # Tron leotards
    pass

else:  # Amiga/Atari - The Wonder Computer of the 1980s :-D
    log.warn('Unexpected OS: os.name: %s', os_name)


if __name__ == '__main__':

    # logs the detection information sequence
    print()  # space from warnings

    try:
        import out
        out.configure(level='debug')
    except ImportError:
        fmt = '  %(levelname)-7.7s %(module)s/%(funcName)s:%(lineno)s %(message)s'
        logging.basicConfig(level=logging.DEBUG, format=fmt)

    choose_palette()
