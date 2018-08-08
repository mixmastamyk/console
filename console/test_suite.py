'''
    console - An easy to use ANSI escape sequence library.
    © 2018, Mike Miller - Released under the LGPL, version 3+.

    Testen-Sie, bitte.
'''
import pytest

from . import style, _set_debug_mode

# configure our own - force all palettes on
args = dict(autodetect=False, palettes=('basic', 'extended', 'truecolor'))

fg = style.ForegroundPalette(**args)
bg = style.BackgroundPalette(**args)
fx = style.EffectsPalette(**args)
defx = style.EffectsTerminator(**args)

fg, bg, fx, pytest  # pyflakes

# beginning of tests
_set_debug_mode(True)


# Basic palette - fg
# ----------------------------------------------------------------------------
if True:  # fold

    def test_fgbasic():

        assert str(fg.default)      ==  '\x1b[39m'
        assert str(fg.black)        ==  '\x1b[30m'
        assert str(fg.red)          ==  '\x1b[31m'
        assert str(fg.green)        ==  '\x1b[32m'
        assert str(fg.yellow)       ==  '\x1b[33m'
        assert str(fg.blue)         ==  '\x1b[34m'
        assert str(fg.magenta)      ==  '\x1b[35m'
        assert str(fg.purple)       ==  '\x1b[35m'
        assert str(fg.cyan)         ==  '\x1b[36m'
        assert str(fg.white)        ==  '\x1b[37m'

        assert str(fg.lightblack)   ==  '\x1b[90m'
        assert str(fg.lightred)     ==  '\x1b[91m'
        assert str(fg.lightgreen)   ==  '\x1b[92m'
        assert str(fg.lightyellow)  ==  '\x1b[93m'
        assert str(fg.lightblue)    ==  '\x1b[94m'
        assert str(fg.lightmagenta) ==  '\x1b[95m'
        assert str(fg.lightcyan)    ==  '\x1b[96m'
        assert str(fg.lightwhite)   ==  '\x1b[97m'


    def test_bgbasic():

        assert str(bg.default)      ==  '\x1b[49m'
        assert str(bg.black)        ==  '\x1b[40m'
        assert str(bg.red)          ==  '\x1b[41m'
        assert str(bg.green)        ==  '\x1b[42m'
        assert str(bg.yellow)       ==  '\x1b[43m'
        assert str(bg.blue)         ==  '\x1b[44m'
        assert str(bg.magenta)      ==  '\x1b[45m'
        assert str(bg.purple)       ==  '\x1b[45m'
        assert str(bg.cyan)         ==  '\x1b[46m'
        assert str(bg.white)        ==  '\x1b[47m'

        assert str(bg.lightblack)   ==  '\x1b[100m'
        assert str(bg.lightred)     ==  '\x1b[101m'
        assert str(bg.lightgreen)   ==  '\x1b[102m'
        assert str(bg.lightyellow)  ==  '\x1b[103m'
        assert str(bg.lightblue)    ==  '\x1b[104m'
        assert str(bg.lightmagenta) ==  '\x1b[105m'
        assert str(bg.lightcyan)    ==  '\x1b[106m'
        assert str(bg.lightwhite)   ==  '\x1b[107m'


    def test_fxbasic():

        assert str(fx.end)          ==  '\x1b[0m'
        assert str(fx.bold)         ==  '\x1b[1m'
        assert str(fx.dim)          ==  '\x1b[2m'
        assert str(fx.italic)       ==  '\x1b[3m'
        assert str(fx.underline)    ==  '\x1b[4m'
        assert str(fx.slowblink)    ==  '\x1b[5m'
        assert str(fx.fastblink)    ==  '\x1b[6m'
        assert str(fx.reverse)      ==  '\x1b[7m'
        assert str(fx.conceal)      ==  '\x1b[8m'
        assert str(fx.hide)         ==  '\x1b[8m'
        assert str(fx.crossed)      ==  '\x1b[9m'
        assert str(fx.strike)       ==  '\x1b[9m'
        assert str(fx.frame)        ==  '\x1b[51m'
        assert str(fx.encircle)     ==  '\x1b[52m'
        assert str(fx.overline)     ==  '\x1b[53m'

    def test_basic_wrong_name():
        with pytest.raises(AttributeError):
            fg.KERBLOOWIE


# Extended palette - fg
# ----------------------------------------------------------------------------
if True:  # fold

    def test_fgext_too_short():
        with pytest.raises(AttributeError) as err:
            fg.i
        assert 'length' in err.value.args[0]

    def test_fgext_one_digit():

        assert str(fg.i1) ==  '\x1b[38;5;1m'

    def test_fgext_two_digit():

        assert str(fg.i11) == '\x1b[38;5;11m'

    def test_fgext_three_digits():

        assert str(fg.i111) == '\x1b[38;5;111m'

    def test_fgext_four_digits():
        with pytest.raises(AttributeError) as err:
            fg.i1111
        assert 'length' in err.value.args[0]

    # bg
    def test_bgext_too_short():
        with pytest.raises(AttributeError) as err:
            bg.i
        assert 'length' in err.value.args[0]

    def test_bgext_one_digit():

        assert str(bg.i1) ==  '\x1b[48;5;1m'

    def test_bgext_two_digit():

        assert str(bg.i11) == '\x1b[48;5;11m'

    def test_bgext_three_digits():

        assert str(bg.i111) == '\x1b[48;5;111m'

    def test_bgext_too_long():
        with pytest.raises(AttributeError) as err:
            bg.i1111
        assert 'length' in err.value.args[0]


# True color palette - fg
# ----------------------------------------------------------------------------
if True:  # fold

    def test_fgtrue_too_short():
        with pytest.raises(AttributeError) as err:
            fg.tbb00
        assert 'length' in err.value.args[0]

    def test_fgext_three_digits():

        assert str(fg.tb0b) ==  '\x1b[38;2;187;0;187m'

    def test_fgext_six_digits():

        assert str(fg.tff00bb) ==  '\x1b[38;2;255;0;187m'

    def test_fgext_wrong_format():
        with pytest.raises(AttributeError) as err:
            fg.tbob
        assert 'hex digits' in err.value.args[0]

    def test_fgext_too_long():
        with pytest.raises(AttributeError) as err:
            fg.tDEADBEEFCAFE
        assert 'length' in err.value.args[0]

    # bg
    def test_bgtrue_too_short():
        with pytest.raises(AttributeError) as err:
            bg.tbb00
        assert 'length' in err.value.args[0]

    def test_bgext_three_digits():

        assert str(bg.tb0b) ==  '\x1b[48;2;187;0;187m'

    def test_bgext_six_digits():

        assert str(bg.tff00bb) ==  '\x1b[48;2;255;0;187m'

    def test_bgext_wrong_format():
        with pytest.raises(AttributeError) as err:
            bg.tbob
        assert 'hex digits' in err.value.args[0]

    def test_bgext_too_long():
        with pytest.raises(AttributeError) as err:
            bg.tDEADBEEFCAFE
        assert 'length' in err.value.args[0]


# Concat + str
# ----------------------------------------------------------------------------
if True:  # fold

    def test_string_concat_fg():
        text = fg.red + 'RED ' + fg.green + 'GRN ' + fg.blue + 'BLU' + fg.default
        assert text == '\x1b[31mRED \x1b[32mGRN \x1b[34mBLU\x1b[39m'

    def test_string_concat_bg():
        text = bg.yellow + 'YEL ' + bg.magenta + 'MAG ' + bg.cyan + 'CYN' + bg.default
        assert text == '\x1b[43mYEL \x1b[45mMAG \x1b[46mCYN\x1b[49m'

    def test_string_concat_fx():
        text = fx.bold + 'BLD ' + fx.underline + 'UND ' + fx.reverse + 'REV' + fx.end
        assert text == '\x1b[1mBLD \x1b[4mUND \x1b[7mREV\x1b[0m'


# Concat + objects
# ----------------------------------------------------------------------------
if True:  # fold
        #~ print(f'{text!r} → {text}')

    def test_attribute_multiple_addition_no_accumulation():
        # make style with addition
        muy_importante = fg.white + fx.bold + bg.red
        # use
        text = muy_importante + ' ARRIBA! ' + fx.end
        assert text == '\x1b[37;1;41m ARRIBA! \x1b[0m'

        # important check:
        # fg.white should not be affected, since we returned a new obj on add
        text = fg.white + 'FOO' + fx.end
        assert text == '\x1b[37mFOO\x1b[0m'


# Call
# ----------------------------------------------------------------------------
if True:  # fold

    def test_attribute_call():
        text = bg.purple('⛈ PURPLE RAIN ⛈')

        #~ assert text == '\x1b[45m⛈ PURPLE\xa0RAIN ⛈\x1b[49m'
        assert text == '\x1b[45m⛈ PURPLE\xa0RAIN ⛈\x1b[0m'

    def test_attribute_call_plus_styles():
        linkstyle = fg.blue + fx.underline
        text = linkstyle('http://expertsexchange.com/', fx.blink)
        assert text == '\x1b[34;4;5mhttp://expertsexchange.com/\x1b[0m'

# todo: problem
    def test_attribute_call_plus_styles():
        # make style with addition
        muy_importante = fg.white + fx.bold + bg.red
        text = muy_importante('ARRIBA!')
        assert text == '\x1b[37;1;41mARRIBA!\x1b[0m'


