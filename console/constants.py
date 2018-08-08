'''
    console - An easy to use ANSI escape sequence library.
    © 2018, Mike Miller - Released under the LGPL, version 3+.

    Important constants needed all over the code.

    Placing in a separate module avoids circular imports.
'''

BEL = '\a'          #   7   007   0x07   ^G  Terminal bell - Ding!
BS  = '\b'          #   8   010   0x08   ^H  Backspace
HT  = '\t'          #   9   011   0x09   ^I  Horizontal TAB
LF  = '\n'          #  10   012   0x0A   ^J  Linefeed (newline)
VT  = '\v'          #  11   013   0x0B   ^K  Vertical TAB
FF  = '\f'          #  12   014   0x0C   ^L  Formfeed (also: New page NP)
CR  = '\r'          #  13   015   0x0D   ^M  Carriage return
ESC = '\033'        #  27   033   0x1B   ^[  Escape character
DEL = '\177'        # 127   177   0x7F       Delete character

CSI = ESC + '['     # Control Sequence Introducer
OSC = ESC + ']'     # Operating System Command
RIS = ESC + 'c'     # Reset to Initial State, aka clear screen (see utils)

__version__ = '0.80'


if __name__ == '__main__':

    # print constants for convenience
    print('\nConstants:\n')
    _locals = locals()      # avoids issues
    for key in dir():
        if not key.startswith('_'):
            print('%05s = %r' % (key, _locals[key]))
