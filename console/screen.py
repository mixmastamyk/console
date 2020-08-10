# -*- coding: future_fstrings -*-
'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    This module generates ANSI character codes to manage terminal screens and
    move the cursor around.

    Note: The attributes of the Screen container currently are not directly
    composable with the core._PaletteEntry due to the fact that many of them
    need parameters.  This may change in the future.

    Context-managers with contextlib inspired by:

    .. code-block:: text

        blessings.__init__.py
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        A thin, practical wrapper around terminal coloring, styling, and
        positioning.

        :copyright: Copyright 2011-2018, Erik Rose
        :license: MIT License (MIT)

    Note: these could probably be loaded from curses/terminfo,
          but haven't yet found a need.

    TODO:  These objects don't compose like the core objects.
'''
import sys
from contextlib import contextmanager

from . import _CHOSEN_PALETTE
from .constants import CSI, ESC, RIS
from .disabled import empty_bin


class _TemplateString(str):  # Callable[[str], str]
    ''' A template string that renders itself with default arguments when
        created, and may also be called with other arguments.
    '''
    def __new__(cls, endcode, arg='%d'):
        self = str.__new__(cls, CSI + arg + endcode)
        self.endcode = endcode
        return self

    def __call__(self, *args):
        return self % args

    def __str__(self):
        try:
            return self % 1  # default move 1 cell
        except TypeError:
            return self


class Screen:
    ''' Convenience class for cursor and screen manipulation.

        https://en.wikipedia.org/wiki/ANSI_escape_code#CSI_sequences
    '''
    up          = cuu = 'A'
    down        = cud = 'B'
    right       = cuf = forward = 'C'
    left        = cub = backward = 'D'

    next_line   = cnl = 'E'
    prev_line   = cpl = 'F'

    mv_x        = cha = hpa = 'G'
    mv_y        = cva = vpa = 'd'
    mv          = cup = ('H', '%d;%d')      # double trouble - move to pos
    mv2         = hvp = ('f', '%d;%d')      # ""

    erase       = ed = 'J'
    erase_line  = el = 'K'

    scroll_up   = su = 'S'
    scroll_down = sd = 'T'

    save_title  = ('t', '22;%d')
    restore_title = ('t', '23;%d')

    # The following don't need parameter wrapping.  All start with ESC
    auxoff      = CSI + '4i'
    auxon       = CSI + '5i'
    dsr         = loc = CSI + '6n'          # device status rpt, see detection

    reset       = RIS                       # Esc + c

    # cursor config
    save_pos    = ESC + '7'                 # position
    rest_pos    = ESC + '8'
    save_pos2   = scp = CSI + 's'
    rest_pos2   = rcp = CSI + 'u'

    # DEC Private Mode Set (DECSET)
    # https://invisible-island.net/xterm/ctlseqs/ctlseqs.html#h3-Functions-using-CSI-_-ordered-by-the-final-character_s_
    show_cursor = CSI + '?25h'
    hide_cursor = CSI + '?25l'

    reverse_video = CSI + '?5h'  # "flash" screen
    normal_video = CSI + '?5l'

    # https://cirw.in/blog/bracketed-paste
    bracketedpaste_enable = bpon = CSI + '?2004h'
    bracketedpaste_disable = bpoff = CSI + '?2004l'

    alt_screen_enable = ason = CSI + '?1049h'
    alt_screen_disable = asoff = CSI + '?1049l'

    def __new__(cls, force=False):
        ''' Override new() to replace the class entirely on deactivation.

            Complies with palette detection, unless force is on:

            Arguments:
                force           - Force on.
        '''
        self = super().__new__(cls)

        if not force:
            if not _CHOSEN_PALETTE:
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

    def __enter__(self):
        ''' Go full-screen and save title. '''
        self._stream.write(self.alt_screen_enable)
        self._stream.write(str(self.save_title(0)))     # 0 = both icon, title
        self._stream.flush()
        return self

    def __exit__(self, type_, value, traceback):
        ''' Return to normal screen, restore title. '''
        self._stream.write(self.alt_screen_disable)
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
        stream.write(self.alt_screen_enable)
        stream.write(str(self.save_title(0)))     # 0 = both icon, title
        stream.flush()
        try:
            yield self
        finally:
            stream.write(self.alt_screen_disable)
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
        stream.write(self.save_pos)  # cursor position

        if x is not None and y is not None:
            stream.write(self.mv(y, x))
        elif x is not None:
            stream.write(self.mv_x(x))
        elif y is not None:
            stream.write(self.mv_y(y))

        stream.flush()
        try:
            yield self
        finally:
            stream.write(self.rest_pos)
            stream.flush()

    @contextmanager
    def rare_mode(self):
        ''' Context Manager that temporarily turns off echo and line-editing
            functionality; still recognizes Ctrl-C break, Ctrl-Z suspend, etc.
            Also known as "cbreak" mode.

            POSIX only. See getpass for a simple function.

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
            to raw mode.

            POSIX only.
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


# It's Automatic:  https://youtu.be/y5ybok6ZGXk
sc = Screen()
