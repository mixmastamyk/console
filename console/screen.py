'''
    .. console - Comprehensive escape sequence utility library for terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    This module generates ANSI character codes to move the cursor around,
    and terminal windows.

    TODO::

        with term.fullscreen():
            # Print some stuff.
'''
from . import _CHOSEN_PALETTE
from .constants import CSI, ESC
from .disabled import dummy


class _TemplateString(str):
    ''' A template string that renders itself with default arguments when
        created, and may also be called with another argument.

        TODO: reconcile with core classes.
    '''
    def __new__(cls, code, arg='%d'):
        self = str.__new__(cls, CSI + arg + code)
        self.code = code
        return self

    def __call__(self, *args):
        return self % args

    def __str__(self):
        try:
            return self % 1  # default move 1 cell
        except TypeError as err:
            return self


class Screen:
    ''' Convenience class for cursor and screen manipulation.

        https://en.wikipedia.org/wiki/ANSI_escape_code#CSI_sequences
    '''
    up          = cuu = 'A'
    down        = cud = 'B'
    right       = cuf = forward = 'C'
    left        = cub = backward = 'D'

    nextline    = cnl = 'E'
    prevline    = cpl = 'F'

    horizabs    = cha = 'G'

    cup         = mv = ('H', '%d;%d')       # double trouble - move to pos
    hvp         = ('f', '%d;%d')            # ""

    erase       = ed = 'J'
    eraseline   = el = 'K'

    scrollup    = su = 'S'
    scrolldown  = sd = 'T'

    # These don't need wrapping, all start with ESC
    auxoff      = CSI + '4i'
    auxon       = CSI + '5i'
    dsr         = loc = CSI + '6n'          # device status report,
    savepos     = scp = CSI + 's'           # ↑ i.e. cursor location
    restpos     = rcp = CSI + 'u'

    save        = CSI + '?47h'                  # whole screen
    restore     = CSI + '?47l'                  # ""
    reset       = ESC + 'c'                     # ""

    # https://cirw.in/blog/bracketed-paste
    bracketedpaste_enable = bpon = CSI + '?2004h'
    bracketedpaste_disable = bpoff = CSI + '?2004l'


    def __new__(cls, autodetect=True, force=False):
        ''' Override new() to replace the class entirely on deactivation.

            Arguments:
                autodetect      - Attempt to detect palette support.
                force           - Force on.
        '''
        self = super().__new__(cls)

        if autodetect and not force:
            if not _CHOSEN_PALETTE:
                self = dummy        # None, deactivate completely
        # else: continue on unabated

        return self

    def __init__(self, **kwargs):
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


screen = Screen()
