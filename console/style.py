'''
    console - Comprehensive escape sequence utility library for terminals.
    © 2018, Mike Miller - Released under the LGPL, version 3+.

        Module inspired by: colorama.ansi.py © Jonathan Hartley 2013.

    This module is focused on the escape codes concerning character styles
    and colors interpreted by terminals, sometimes called
    "SGR (Select Graphic Rendition) parameters."

    There are a number of classes to facilitate using them.

    See: http://en.wikipedia.org/wiki/_escape_code
         and section 5:
         #SGR_(Select_Graphic_Rendition)_parameters
'''
from .core import _BasicPaletteBuilder, _HighColorPaletteBuilder


class ForegroundPalette(_HighColorPaletteBuilder):
    ''' Container for ANSI foreground color codes. '''

    default         = 39    # must be first :-D

    black           = 30
    red             = 31
    green           = 32
    yellow          = 33
    blue            = 34
    magenta         = 35
    purple          = magenta
    cyan            = 36
    white           = 37

    # aixterm, bright colors without bold - widely supported, not official
    lightblack      = 90
    lightred        = 91
    lightgreen      = 92
    lightyellow     = 93
    lightblue       = 94
    lightmagenta    = 95
    lightcyan       = 96
    lightwhite      = 97

    # extended      = 38
    _start_codes_extended = '38;5'
    _start_codes_true = '38;2'


class BackgroundPalette(_HighColorPaletteBuilder):
    ''' Container for ANSI background color codes. '''
    default         = 49

    black           = 40
    red             = 41
    green           = 42
    yellow          = 43
    blue            = 44
    magenta         = 45
    purple          = magenta
    cyan            = 46
    white           = 47

    # aixterm, bright colors without bold - widely supported, not official
    lightblack      = 100
    lightred        = 101
    lightgreen      = 102
    lightyellow     = 103
    lightblue       = 104
    lightmagenta    = 105
    lightcyan       = 106
    lightwhite      = 107

    # extended      = 48
    _start_codes_extended = '48;5'
    _start_codes_true = '48;2'


class EffectsPalette(_BasicPaletteBuilder):
    ''' Container for ANSI for text style codes.

        Bold, italic, underline, blink, reverse, strike, fonts, etc.
    '''
    end = default   = 0  # reset all

    bold            = 1
    b               = 1  # short
    dim             = 2
    italic          = 3
    i               = 3  # short
    underline       = 4
    u               = 4  # short
    blink           = 5
    slowblink       = blink
    fastblink       = 6
    reverse         = 7
    conceal         = 8
    hide            = conceal
    crossed         = 9
    strike          = crossed

    frame           = 51
    encircle        = 52
    overline        = 53

    # Rarely used codes to change fonts, unlikely to be supported:
    font10          = 10
    font11          = 11
    font12          = 12
    font13          = 13
    font14          = 14
    font15          = 15
    font16          = 16
    font17          = 17
    font18          = 18
    font19          = 19
    font20          = 20

    primary         = font10
    fraktur         = font20

    # should these ideogram codes be enabled?
    # ideogramurl     = 60
    # ideogramdrl     = 61
    # ideogramoll     = 62
    # ideogramdll     = 63
    # ideogramst      = 64


class EffectsTerminator(_BasicPaletteBuilder):
    ''' "I'll be baahhck."

        Rarely used codes to turn off specific style features, not supported at
        times.  Generally, use of EffectsPalette.end is simpler and more
        reliable.
    '''
    # convenience:
    end             = 0
    fg              = ForegroundPalette.default
    bg              = BackgroundPalette.default

    bold            = 21
    intensity       = 22  # bold, dim (maybe color) ---> norm
    italic = font   = 23
    underline       = 24
    blink           = 25
    reverse         = 27
    reveal          = 28
    crossed         = 29
    strike          = crossed

    frame           = 54
    encircle        = frame
    overline        = 55
    ideogram        = 65


fg = ForegroundPalette()
bg = BackgroundPalette()

fx = EffectsPalette()
defx = EffectsTerminator()
