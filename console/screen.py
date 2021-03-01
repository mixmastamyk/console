# -*- coding: future_fstrings -*-
'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    This module generates ANSI character codes to manage terminal screens and
    move the cursor around.

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

from . import _term_level
from .constants import CSI, ESC, RIS
from .disabled import empty_bin


# Mapping of convenience names to terminfo capabilities:
NAME_TO_TINFO_MAP = dict(
    up          = 'cuu',
    down        = 'cud',
    right       = 'cuf',
    forward     = 'cuf',
    left        = 'cub',
    backward    = 'cub',

    clear       = 'ed',
    clear_line  = 'el',
    erase_char  = 'ech',
    insert_line = 'il',
    delete_char = 'dch',
    delete_line = 'dl',

    move_to     = 'cup',
    move_x      = 'hpa',
    move_y      = 'vpa',
    scroll_down = 'sd',
    scroll_up   = 'su',

    hide_cursor = 'civis',
    show_cursor = 'cnorm',
    save_cursor = 'sc',
    restore_cursor = 'rc',

    enable_alt_screen  = 'smcup',
    disable_alt_screen = 'rmcup',

)


class _ContextMixin:
    ''' Various context handlers are defined here. '''
    # The following don't need parameter wrapping, all start with ESC
    sc      = ESC + '7'  # save cursor position
    rc      = ESC + '8'  # restore

    cnorm   = CSI + '?25h'
    civis   = CSI + '?25l'

    # alt screen
    smcup = CSI + '?1049h'
    rmcup = CSI + '?1049l'

    # -- below don't yet have terminfo names ---------------------------------
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
        self._stream.write(str(self.save_title(0)))     # 0 = both icon, title
        self._stream.flush()
        return self

    def __exit__(self, type_, value, traceback):
        ''' Return to normal screen, restore title. '''
        self._stream.write(self.disable_alt_screen)
        self._stream.write(str(self.restore_title(0)))  # 0 = both icon, title
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
        stream.write(self.bracketedpaste_enable)
        stream.flush()
        try:
            yield self
        finally:
            stream.write(self.bracketedpaste_disable)
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
        stream.write(str(self.save_title(0)))     # 0 = both icon, title
        stream.flush()
        try:
            yield self
        finally:
            stream.write(self.disable_alt_screen)
            stream.write(str(self.restore_title(0)))  # 0 = icon & title
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
        stream.write(self.save_cursor)  # cursor position

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
            stream.write(self.restore_cursor)
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

        fd = self._stream.fileno()
        orig_attrs = termios.tcgetattr(fd)      # save
        termios.tcflush(fd, termios.TCIFLUSH)   # clear input
        tty.setcbreak(fd, termios.TCSANOW)      # aka rare mode
        try:
            yield self                          # wait

        finally:  # restore
            termios.tcsetattr(fd, termios.TCSADRAIN, orig_attrs)

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

        fd = self._stream.fileno()
        orig_attrs = termios.tcgetattr(fd)      # save
        termios.tcflush(fd, termios.TCIFLUSH)   # clear input
        tty.setraw(fd, termios.TCSANOW)
        try:
            yield self                          # wait
        finally:  # restore
            termios.tcsetattr(fd, termios.TCSADRAIN, orig_attrs)


class Screen(_ContextMixin):
    ''' Convenience class for cursor and screen manipulation.

        https://en.wikipedia.org/wiki/ANSI_escape_code#CSI_sequences
    '''
    cuu = 'A'
    cud = 'B'
    cuf = 'C'
    cub = 'D'

    cnl = 'E'  # col 1
    cpl = 'F'  # col 1

    hpa = 'G'  # cha not set?
    cup = ('H', '%s;%s')      # double trouble - move to pos

    vpa = 'd'  # cva?
    hvp = ('f', '%s;%s')      # ""

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

    # The following don't need parameter wrapping, start with ESC
    loc = CSI + '6n'                # see detection
    reset = RIS                     # Esc + c

    def __new__(cls, force=False):
        ''' Override new() to replace the class entirely on deactivation.

            Complies with palette detection, unless force is on:

            Arguments:
                force           - Force on.
        '''
        self = super().__new__(cls)

        if not force:
            if not _term_level:
                self = empty_bin    # None, deactivate completely
        # else: continue on unabated
        return self

    def __init__(self, stream=sys.stdout, **kwargs):
        self._stream = stream
        # look for attributes to wrap in a _TemplateString:
        for name in dir(self):
            if not name.startswith('_'):
                value = getattr(self, name)

                if type(value) is str and not value.startswith(ESC):
                    attr = _TemplateString(value)
                    setattr(self, name, attr)

                elif type(value) is tuple:
                    attr = _TemplateString(*value)
                    setattr(self, name, attr)

    def __getattr__(self, attr):
        # when attr missing, look in convenience map
        capability_name = NAME_TO_TINFO_MAP.get(attr)
        if capability_name:  # cache and return
            value = getattr(self, capability_name)
            setattr(self, attr, value)
            return value
        else:
            class_name = self.__class__.__name__
            msg = f'{class_name!r} object has no attribute {attr!r}'
            raise AttributeError(msg)


class _TemplateString(str):  # Callable[[str], str]
    ''' A template string that renders itself with given or default arguments.
    '''
    _default = 1

    def __new__(cls, endcode, arg='%s'):
        self = str.__new__(cls, CSI + arg + endcode)
        self.endcode = endcode
        return self

    def __call__(self, *args):
        return self % args

    def __str__(self):
        try:
            return self % self._default  # default move 1 cell
        except TypeError:
            return self


# It's Automatic:  https://youtu.be/y5ybok6ZGXk
sc = Screen()
