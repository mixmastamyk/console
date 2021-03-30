# -*- coding: future_fstrings -*-
'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    This module generates ANSI character codes to manage terminal screens and
    move the cursor around, via a Screen class.

    For the cursor and view "move to" instruction,
    Screen classes default to standard (x, y) coordinate order and also use
    0-based locations as does Python curses.
    This means the coordinates of the the ``cup`` and ``hvp`` instructions
    will also have 1 added to each value on output.

    If you'd prefer a (y, x) coordinate order as in the ANSI/Curses sequences,
    pass the parameter swap=False on initialization.

    Context-managers with contextlib inspired by:

    .. code-block:: text

        blessings.__init__.py
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        A thin, practical wrapper around terminal coloring, styling, and
        positioning.

        :copyright: Copyright 2011-2018, Erik Rose
        :license: MIT License (MIT)

'''
import sys
from contextlib import contextmanager

from . import ansi_capable as _ansi_capable, using_terminfo
from .constants import CSI, ESC, RIS
from .detection import get_position as _get_position, TermStack


# Mapping of convenience names to terminfo capabilities,
# using verb_object form:
NAME_TO_TERMINFO_MAP = dict(
    clear               = 'ed',
    clear_line          = 'el',
    delete_char         = 'dch',
    delete_line         = 'dl',
    erase_char          = 'ech',
    insert_line         = 'il',
    reset               = 'rs1',

    move_to             = 'cup',
    move_x              = 'hpa',
    move_y              = 'vpa',
    move_up             = 'cuu',
    move_down           = 'cud',
    move_right          = 'cuf',
    move_forward        = 'cuf',
    move_left           = 'cub',
    move_backward       = 'cub',
    scroll_down         = 'sd',
    scroll_up           = 'su',

    hide_cursor         = 'civis',
    show_cursor         = 'cnorm',
    save_cursor         = 'sc',     # color as well
    save_position       = 'sc',     # alias
    restore_cursor      = 'rc',     # alias
    restore_position    = 'rc',

    enable_alt_screen   = 'smcup',
    disable_alt_screen  = 'rmcup',
)


class _ContextMixin:
    ''' Various Blessings-inspired context handlers are defined here. '''

    # these don't have terminfo names to associate with
    enable_flash = CSI + '?5h'      # terminfo cap name, only single "flash"
    disable_flash = CSI + '?5l'

    # https://cirw.in/blog/bracketed-paste
    enable_bracketed_paste = CSI + '?2004h'
    disable_bracketed_paste = CSI + '?2004l'

    save_title = ('t', '22;%s')
    restore_title =  ('t', '23;%s')

    def __enter__(self):
        ''' Go full-screen and save title. '''
        self._stream.write(self.enable_alt_screen)
        self._stream.write(self.save_title(0))          # 0 = both icon, title
        self._stream.flush()
        return self

    def __exit__(self, type_, value, traceback):
        ''' Return to normal screen, restore title. '''
        self._stream.write(self.disable_alt_screen)
        self._stream.write(self.restore_title(0))       # 0 = both icon, title
        self._stream.flush()

    @contextmanager
    def bracketed_paste(self):
        ''' Context Manager that brackets-the-paste:

            - https://cirw.in/blog/bracketed-paste
            - https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h2-Bracketed-Paste-Mode

            .. code-block:: python

                with screen.bracketed_paste():
                    print('Hit me with your best shot…')
        '''
        stream = self._stream
        stream.write(self.enable_bracketed_paste)
        stream.flush()
        try:
            yield self
        finally:
            stream.write(self.disable_bracketed_paste)
            stream.flush()

    @contextmanager
    def fullscreen(self):
        ''' Context Manager that enters full-screen mode and restores normal
            mode on exit.

            .. code-block:: python

                with screen.fullscreen():
                    print('Hello, world!')
        '''
        stream = self._stream
        stream.write(self.enable_alt_screen)
        stream.write(self.save_title(0))            # 0 = both icon, title
        stream.flush()
        try:
            yield self
        finally:
            stream.write(self.disable_alt_screen)
            stream.write(self.restore_title(0))     # 0 = icon & title
            stream.flush()

    @contextmanager
    def hidden_cursor(self):
        ''' Context Manager that hides the cursor and restores it on exit.

            .. code-block:: python

                with screen.hidden_cursor():
                    print('Clandestine activity…')
        '''
        stream = self._stream
        stream.write(self.hide_cursor)
        stream.flush()
        try:
            yield self
        finally:
            stream.write(self.show_cursor)
            stream.flush()

    @contextmanager
    def location(self, x=None, y=None):
        ''' Temporarily move the cursor, perform work, and return to the
            previous location.

            ::

                with screen.location(40, 20):
                    print('Hello, world!')
        '''
        stream = self._stream
        stream.write(self.save_position)

        if x is not None and y is not None:
            stream.write(self.move_to(y, x))
        elif x is not None:
            stream.write(self.move_x(x))
        elif y is not None:
            stream.write(self.move_y(y))

        stream.flush()
        try:
            yield self
        finally:
            stream.write(self.restore_position)
            stream.flush()

    @contextmanager
    def rare_mode(self):
        ''' Context Manager that temporarily turns off echo and line-editing
            functionality; still recognizes Ctrl-C break, Ctrl-Z suspend, etc.
            Also known as "cbreak" mode.  POSIX only.

            See getpass for a usage example.

            .. code-block:: python

                with screen.rare_mode():
                    read_keys()
        '''
        import termios, tty  # defer

        with TermStack() as fd:
            termios.tcflush(fd, termios.TCIFLUSH)   # clear Input
            tty.setcbreak(fd, termios.TCSANOW)
            yield self                              # wait

    @contextmanager
    def raw_mode(self):
        ''' Context Manager that temporarily that temporarily sets terminal
            to raw mode. POSIX only.

            See utils.wait_key() if looking for a simple read-key function.

            .. code-block:: python

                with screen.raw_mode():
                    read_raw_keypresses()
        '''
        import termios, tty  # defer

        with TermStack() as fd:
            termios.tcflush(fd, termios.TCIFLUSH)   # clear Input
            tty.setraw(fd, termios.TCSANOW)
            yield self                              # wait


class Screen(_ContextMixin):
    ''' Convenience class for cursor and screen manipulation.

        Short names (terminfo capnames) are defined below,
        while the NAME_TO_TERMINFO_MAP mapping defines easier to remember
        verbose names.

        ScreenTermInfo defaults to standard (x, y) coordinate order and uses
        0-based locations as does Python curses.

        Example::

            from console.screen import sc

            >>> sc.move_to
            '\x1b[%s;%sH'

            >>> sc.move_to(3, 6)
            '\x1b[7;4H'  # swapped and incremented to ANSI format.


        https://en.wikipedia.org/wiki/ANSI_escape_code#CSI_sequences
    '''
    # The class attributes below will be wrapped with a _TemplateString on init
    cuu = 'A'
    cud = 'B'
    cuf = 'C'
    cub = 'D'

    cnl = 'E'  # col 1
    cpl = 'F'  # col 1

    hpa = 'G'  # cha?
    cup = ('H', '%s;%s')      # double trouble - move to pos

    vpa = 'd'  # cva?
    hvp = ('f', '%s;%s')      # "", appears to move the view rather than cursor

    cht = 'I'
    ed  = 'J'    # clear, 1 from start, 2 whole, 3 scrollback
    el  = 'K'    # line

    ich = '@'
    il  = 'L'
    dl  = 'M'
    dch = 'P'

    su  = 'S'
    sd  = 'T'

    ech = 'X'
    cbt = 'Z'

    # The following don't need parameter wrapping, all start with ESC
    rs1 = RIS
    sc  = ESC + '7'  # save cursor position
    rc  = ESC + '8'  # restore

    cnorm = CSI + '?25h'
    civis = CSI + '?25l'

    # alt screen
    smcup = CSI + '?1049h'
    rmcup = CSI + '?1049l'


    def __new__(cls, force=None, **kwargs):
        ''' Override new() to replace the class entirely on deactivation.

            Complies with terminal level detection, unless force is on:

            Arguments:
                force           - Force sequences on.
        '''
        if _ansi_capable or force:
            self = super().__new__(cls)
        else:
            from .disabled import empty_scr_bin
            # Makes new empties to deactivate completely:
            self = empty_scr_bin

        return self

    def __init__(self, stream=sys.stdout, swap=True, **kwargs):
        '''
            Arguments:
                stream          - For context managers
                swap            - Coordinate order, i.e. Given in:
                                    True    # Standard order, needs swapping.
                                    False   # ANSI/Curses format
        '''
        self._stream = stream

        # look for attributes to wrap in a _TemplateString:
        for name in dir(self):
            if not name.startswith('_'):
                value = getattr(self, name)

                if type(value) is str and not value.startswith(ESC):
                    attr = _TemplateString(value)
                    setattr(self, name, attr)

                # only cup and hvp need to worry about coordinates:
                elif type(value) is tuple:
                    attr = _TemplateString(*value, swap=swap)
                    setattr(self, name, attr)

    def __getattr__(self, attr):
        # when attr is *missing*, look in convenience map:
        cap_name = NAME_TO_TERMINFO_MAP.get(attr)
        if cap_name:
            value = getattr(self, cap_name)
            setattr(self, attr, value)  # cache
            return value
        else:
            class_name = self.__class__.__name__
            msg = f'{class_name!r} object has no attribute {attr!r}'
            raise AttributeError(msg)


class _TemplateString(str):
    ''' A template string that renders itself with given or default args. '''
    _default = 1

    def __new__(cls, endcode, arg='%s', swap=None):
        self = str.__new__(cls, CSI + arg + endcode)
        self.endcode = endcode  # used in test
        self._swap = swap
        return self

    def __call__(self, *args):
        if len(args) == 2:
            if self._swap:  # swap standard coordinate order backwards
                args = args[::-1]
            args = (args[0] + 1, args[1] + 1)  # use 1-based coordinate origin
        return self % args

    def __str__(self):
        try:
            return self % self._default  # default move 1 cell
        except TypeError:
            return self


class ScreenTermInfo(_ContextMixin):
    ''' Convenience class for cursor and screen manipulation.

        Short names (terminfo capnames) are available,
        while the NAME_TO_TERMINFO_MAP mapping defines several easier to
        remember verbose names.

        This implementation uses Terminfo instead of hard-coded ANSI sequences.

        ScreenTermInfo defaults to standard (x, y) coordinate order and uses
        0-based locations as does Python curses.
        Use swap=False to reverse that.

        Example::

            >>> sc.move_to
            '\x1b[%i%p1%d;%p2%dH'

            >>> sc.move_to(3, 6)
            '\x1b[7;4H'  # swap and incremented to ANSI format.

        https://en.wikipedia.org/wiki/Terminfo
    '''
    def __new__(cls, force=False, **kwargs):
        ''' Override new() to replace the class entirely on deactivation.

            Complies with terminfo details, unless force is on:

            Arguments:
                force           - Force on.
        '''
        if _ansi_capable or force:
            self = super().__new__(cls)
        else:
            from .disabled import empty_scr_bin
            # Makes new empties to deactivate completely:
            self = empty_scr_bin

        return self

    def __init__(self, stream=sys.stdout, swap=True, **kwargs):
        '''
            Arguments:
                stream          - For context managers
                swap            - Coordinate order, i.e. Given in:
                                    True    # Standard order, needs swapping.
                                    False   # ANSI/Curses format
        '''
        self._stream = stream
        self._swap = swap

    def __getattr__(self, attr):
        # when attribute is *missing*
        if using_terminfo:
            cap_name = NAME_TO_TERMINFO_MAP.get(attr, attr)

            # search terminfo
            value = None
            for get_cap in _ti_query_functions:
                value = get_cap(cap_name)
                if value is None:
                    continue
                elif value in (-1, -2):
                    value = None
                else:  # found
                    break

            if value is None:  # didn't find it, return None or raise?
                #~ class_name = self.__class__.__name__
                #~ raise AttributeError(f'{class_name!r} object has no attribute {cap_name!r}')
                pass
            else:  # convert, cache, and return
                if b'%' in value:  # tparm!
                    value = _TemplateStringTermInfo(value, swap=self._swap)
                else:
                    value = value.decode('ascii')

                setattr(self, cap_name, value)  # short name
                if cap_name != attr:  # long name also
                    setattr(self, attr, value)
            return value
        else:
            raise RuntimeError('Terminfo is not available, use the standard '
                               'Screen class instead.')


class _TemplateStringTermInfo(str):
    ''' A callable template string that renders itself with given args. '''

    def __new__(cls, value, swap=None):
        self = str.__new__(cls, value.decode('ascii'))  # as str
        self._byte_str = value  # orig as bytes
        self._swap = swap
        return self

    def __call__(self, *args):
        ''' Run the tparm! '''
        if len(args) == 2 and self._swap:
            args = args[::-1]  # swap standard coordinate order backwards
        return _tparm(self._byte_str, *args).decode('ascii')  # to string


# Rather than define get_position() under Screen*,
# we let detection pick the implementation,
# as it is different under Windows.  Then we attach it here.
if _ansi_capable:
    Screen.get_position = ScreenTermInfo.get_position = (
        staticmethod(_get_position)
    )
else:
    from .meta import defaults
    Screen.get_position = ScreenTermInfo.get_position = (
        lambda *args, **kwargs: defaults.CURSOR_POS_FALLBACK
    )


# It's Automatic:  https://youtu.be/y5ybok6ZGXk
if using_terminfo:
    from . import _curses

    _ti_query_functions = (
        _curses.tigetstr, _curses.tigetnum, _curses.tigetflag
    )
    _tparm = _curses.tparm
    sc = ScreenTermInfo()
else:
    sc = Screen()
