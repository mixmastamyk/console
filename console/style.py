'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    .. Module inspired by: colorama.ansi.py © Jonathan Hartley 2013.

    This module is focused on the escape codes concerning character styles and
    colors interpreted by terminals, sometimes called
    "SGR (Select Graphic Rendition) parameters."

    A number of classes below facilitate using them.  See:

    - `ANSI escape codes
      <https://en.wikipedia.org/wiki/ANSI_escape_code>`_
      and section 5:
'''
from .core import _MonochromePaletteBuilder, _HighColorPaletteBuilder
from .constants import (ANSI_BG_LO_BASE, ANSI_BG_HI_BASE, ANSI_FG_LO_BASE,
                        ANSI_FG_HI_BASE)


class ForegroundPalette(_HighColorPaletteBuilder):
    ''' Container for foreground color codes.

        Arguments:
            autodetect          - Attempt to detect palette support.
            palettes            - If autodetect disabled, set palette support
                                  explicitly.  str, seq, or None

        See:
            https://en.wikipedia.org/wiki/ANSI_escape_code#3/4_bit
    '''
    default         = 39    # must be first :-D

    black           = 30
    red             = 31
    green           = 32
    yellow          = 33
    blue            = 34
    magenta         = 35
    purple          = magenta
    cyan            = 36
    white           = 37

    # aixterm, bright colors without bold - widely supported, but not official
    lightblack      = 90
    lightred        = 91
    lightgreen      = 92
    lightyellow     = 93
    lightblue       = 94
    lightmagenta    = 95
    lightpurple     = lightmagenta
    lightcyan       = 96
    lightwhite      = 97

    # extended      = 38
    _offset_base   = ANSI_FG_LO_BASE   # fbterm transformation
    _offset_base2  = ANSI_FG_HI_BASE   # fbterm transformation
    _start_codes_extended = ('38', '5')
    _start_codes_extended_fbterm = ('1',)
    _start_codes_direct = ('38', '2')


class BackgroundPalette(_HighColorPaletteBuilder):
    ''' Container for background color codes.

        Arguments:
            autodetect          - Attempt to detect palette support.
            palettes            - If autodetect disabled, set palette support
                                  explicitly.  str, seq, or None

        See:
            https://en.wikipedia.org/wiki/ANSI_escape_code#3/4_bit
    '''
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
    lightpurple     = lightmagenta
    lightcyan       = 106
    lightwhite      = 107

    # extended      = 48
    _offset_base    = ANSI_BG_LO_BASE   # fbterm transformation
    _offset_base2   = ANSI_BG_HI_BASE   # fbterm transformation
    _start_codes_extended = ('48', '5')
    _start_codes_extended_fbterm = ('2',)
    _start_codes_direct = ('48', '2')


class UnderlinePalette(_HighColorPaletteBuilder):
    ''' Container for color codes specific to underlines.
        EXPERIMENTAL, see notes.  Supported by libvte and kitty.

        This palette supports extended and true color sequences only.
        However the first 16 colors of extended coincide with standard colors,
        so are available there, e.g.:  `ul.i_0 to ul.i_15`

        Arguments:
            autodetect          - Attempt to detect palette support.
            palettes            - If autodetect disabled, set palette support
                                  explicitly.  str, seq, or None

        Notes:
            https://sw.kovidgoyal.net/kitty/protocol-extensions.html
                #colored-and-styled-underlines
            https://en.wikipedia.org/wiki/ANSI_escape_code#3/4_bit
    '''
    default         = 59

    _start_codes_extended = ('58', '5')
    _start_codes_extended_fbterm = ('2',)
    _start_codes_direct = ('58', '2')

    def __init__(self, color_sep=':', **kwargs):  # uses :
        super().__init__(color_sep=color_sep, **kwargs)


class EffectsTerminator(_MonochromePaletteBuilder):
    ''' *"I'll be baaahhhck."*

        Rarely used codes to turn off *specific* style features, not supported
        at times.  Generally, use of EffectsPalette.end is simpler and more
        reliable.

        Arguments:
            autodetect          - Attempt to detect palette support.
            palettes            - If autodetect disabled, set palette support
                                  explicitly.  str, seq, or None

        See:
            https://en.wikipedia.org/wiki/ANSI_escape_code#SGR_parameters
    '''
    # convenience:
    default = end   = 0
    fg              = ForegroundPalette.default
    bg              = BackgroundPalette.default

    font            = 10
    bold            = 22  # to norm intensity, not bold or dim
    dim             = bold
    italic          = 23
    underline       = 24
    blink           = 25
    # vspacing        = 26  # ?
    reverse         = 27
    conceal         = 28
    hide            = conceal
    crossed         = 29
    strike          = crossed

    # word processor/html shortcuts
    b               = bold
    i               = italic
    s               = crossed
    u               = underline

    frame           = 54
    encircle        = frame
    overline        = 55
    ul_color        = UnderlinePalette.default
    ideogram        = 65


class EffectsPalette(_MonochromePaletteBuilder):
    ''' Container for text style codes.

        Bold, italic, underline, blink, reverse, strike, fonts, etc.

        Arguments:
            autodetect          - Attempt to detect palette support.
            palettes            - If autodetect disabled, set palette support
                                  explicitly.  str, seq, or None

        See:
            https://en.wikipedia.org/wiki/ANSI_escape_code#SGR_parameters
    '''
    default = end   = (0, EffectsTerminator.end)  # reset all

    bold            = (1, EffectsTerminator.bold)
    dim             = (2, EffectsTerminator.dim)
    italic          = (3, EffectsTerminator.italic)
    underline       = (4, EffectsTerminator.underline)
    blink           = (5, EffectsTerminator.blink)
    slowblink       = blink
    fastblink       = (6, EffectsTerminator.blink)
    reverse         = (7, EffectsTerminator.reverse)
    conceal         = (8, EffectsTerminator.conceal)
    hide            = conceal
    crossed         = (9, EffectsTerminator.crossed)
    strike          = crossed

    # word processor/html shortcuts
    b               = bold
    i               = italic
    s               = crossed
    u               = underline

    # Rarely used codes to change fonts, unlikely to be supported:
    #~ font10          = (10, EffectsTerminator.font)  # own terminator?
    #~ font11          = (11, EffectsTerminator.font)
    #~ font12          = (12, EffectsTerminator.font)
    #~ font13          = (13, EffectsTerminator.font)
    #~ font14          = (14, EffectsTerminator.font)
    #~ font15          = (15, EffectsTerminator.font)
    #~ font16          = (16, EffectsTerminator.font)
    #~ font17          = (17, EffectsTerminator.font)
    #~ font18          = (18, EffectsTerminator.font)
    #~ font19          = (19, EffectsTerminator.font)
    #~ font20          = (20, EffectsTerminator.font)
    #~ primary         = font10
    #~ fraktur         = font20

    dunder           = (21, EffectsTerminator.underline)  # orig. disable bold
    double_underline = dunder
    # kitty extensions - https://sw.kovidgoyal.net/kitty/protocol-extensions.html
    # experimental - subject to change, vte also:
    curly_underline  = ('4:3', EffectsTerminator.underline)

    # rarely, if ever implemented
    frame           = (51, EffectsTerminator.frame)
    encircle        = (52, EffectsTerminator.frame)
    overline        = (53, EffectsTerminator.overline)

    # reserved      = 56
    # reserved      = 57

    # should these ideogram codes be enabled?
    # ideogram_ul     = (60, EffectsTerminator.ideogram)  # own terminator?
    # ideogram_du     = (61, EffectsTerminator.ideogram)
    # ideogram_ol     = (62, EffectsTerminator.ideogram)
    # ideogram_do     = (63, EffectsTerminator.ideogram)
    # ideogram_sm     = (64, EffectsTerminator.ideogram)


# It's Automatic:  https://youtu.be/y5ybok6ZGXk
fg = ForegroundPalette()
bg = BackgroundPalette()
ul = UnderlinePalette()

fx = EffectsPalette()
defx = EffectsTerminator()
