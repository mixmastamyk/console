'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    Constants needed cross-package.
'''
from enum import IntEnum as _IntEnum

import env as _env

# ASCII Constants      DEC   OCT    HEX   CTL     DESC
ENQ = '\x05'        #:   5   005           ^E     Enquiry
BEL = '\a'          #:   7   007   0x07    ^G     Terminal bell - Ding!
BS  = '\b'          #:   8   010   0x08    ^H     Backspace
HT  = '\t'          #:   9   011   0x09    ^I     Horizontal TAB
LF  = '\n'          #:  10   012   0x0A    ^J     Linefeed (newline)
VT  = '\v'          #:  11   013   0x0B    ^K     Vertical TAB
FF  = '\f'          #:  12   014   0x0C    ^L     Formfeed (also: New page NP)
CR  = '\r'          #:  13   015   0x0D    ^M     Carriage return

ESC = '\x1b'        #:  27   033           ^[     Escape character
FS  = '\x1c'        #:  28   034                  Field Separator
GS  = '\x1d'        #:  29   035                  Group Separator
RS  = '\x1e'        #:  30   036                  Record Separator

DEL = '\177'        #: 127   177   0x7F           Delete character

# ANSI Constants
CSI = ESC + '['     #: Control Sequence Introducer
OSC = ESC + ']'     #: Operating System Command
RIS = ESC + 'c'     #: Reset to Initial State, aka clear screen (see utils)
ST  = ESC + '\\'    #: Sequence terminator

# some C1 codes, use is problematic under UTF-8 encoding
CSI_C1 = '\x9b'
OSC_C1 = '\x9d'
ST_C1  = '\x9c'


# Where ANSI codes start, floor values:
ANSI_FG_LO_BASE = 30
ANSI_FG_HI_BASE = 90
ANSI_BG_LO_BASE = 40
ANSI_BG_HI_BASE = 100

ANSI_RESET = CSI + '0m'

# Various maps for xterm utils.  Supports integers, though str a bit faster
_COLOR_CODE_MAP = dict(foreground='10', fg='10', background='11', bg='11')
_MODE_MAP = dict(forward='0', backward='1', right='0', left='1', full='2',
                 history='3')
_TITLE_MODE_MAP = dict(both='0', icon='1', title='2')


# Level of functionality provided by the terminal
class TermLevel(_IntEnum):
    DUMB            = 0     # Stream/not a tty, disabled, or ASCII teleprinter
    ANSI_MONOCHROME = 1     # Text effects but no color, e.g. vt220
    ANSI_BASIC      = 2     # + 3,4 Bit, 8/16 indexed colors
    ANSI_EXTENDED   = 3     # + 8 bit, 256 indexed colors
    ANSI_DIRECT     = 4     # + 24 bit, 16m direct colors, aka "true"
    FULL_MONTY      = 9     # + Bleeding edge


if __name__ == '__main__':

    # print constants for convenience
    print('\nConstants:\n')
    _locals = locals()      # avoids issues
    for key in dir():
        if not key.startswith('_'):
            obj = _locals[key]
            if isinstance(obj, type) and issubclass(obj, _IntEnum):
                print('%16s = %r %r' % (key, obj,
                    tuple(m.name for m in TermLevel)))
            else:
                print('%16s = %r' % (key, obj))
