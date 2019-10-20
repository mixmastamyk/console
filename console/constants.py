'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    Constants needed cross-package.
'''
                    #  DEC   OCT    HEX   CTL     DESC
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

CSI = ESC + '['     #: Control Sequence Introducer
OSC = ESC + ']'     #: Operating System Command
RIS = ESC + 'c'     #: Reset to Initial State, aka clear screen (see utils)
ST  = '\\'          #: Sequence terminator, (ESC precedes)

# some C1 codes
CSI_C1 = '\x9b'
OSC_C1 = '\x9d'
ST_C1  = '\x9c'


# Where ANSI codes start, floor values:
ANSI_FG_LO_BASE = 30
ANSI_FG_HI_BASE = 90
ANSI_BG_LO_BASE = 40
ANSI_BG_HI_BASE = 100

ANSI_RESET = CSI + '0m'
ALL_PALETTES = ('basic', 'extended', 'truecolor')  # variants 'x11', 'web'


if __name__ == '__main__':

    # print constants for convenience
    print('\nConstants:\n')
    _locals = locals()      # avoids issues
    for key in dir():
        if not key.startswith('_'):
            print('%16s = %r' % (key, _locals[key]))
