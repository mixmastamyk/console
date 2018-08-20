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
CSI = '\x1b['           # sanity check



# Basic palette - fg
# ----------------------------------------------------------------------------
if True:  # fold

    def test_fgbasic():

        assert str(fg.default)      ==  CSI + '39m'
        assert str(fg.black)        ==  CSI + '30m'
        assert str(fg.red)          ==  CSI + '31m'
        assert str(fg.green)        ==  CSI + '32m'
        assert str(fg.yellow)       ==  CSI + '33m'
        assert str(fg.blue)         ==  CSI + '34m'
        assert str(fg.magenta)      ==  CSI + '35m'
        assert str(fg.purple)       ==  CSI + '35m'
        assert str(fg.cyan)         ==  CSI + '36m'
        assert str(fg.white)        ==  CSI + '37m'

        assert str(fg.lightblack)   ==  CSI + '90m'
        assert str(fg.lightred)     ==  CSI + '91m'
        assert str(fg.lightgreen)   ==  CSI + '92m'
        assert str(fg.lightyellow)  ==  CSI + '93m'
        assert str(fg.lightblue)    ==  CSI + '94m'
        assert str(fg.lightmagenta) ==  CSI + '95m'
        assert str(fg.lightcyan)    ==  CSI + '96m'
        assert str(fg.lightwhite)   ==  CSI + '97m'


    def test_bgbasic():

        assert str(bg.default)      ==  CSI + '49m'
        assert str(bg.black)        ==  CSI + '40m'
        assert str(bg.red)          ==  CSI + '41m'
        assert str(bg.green)        ==  CSI + '42m'
        assert str(bg.yellow)       ==  CSI + '43m'
        assert str(bg.blue)         ==  CSI + '44m'
        assert str(bg.magenta)      ==  CSI + '45m'
        assert str(bg.purple)       ==  CSI + '45m'
        assert str(bg.cyan)         ==  CSI + '46m'
        assert str(bg.white)        ==  CSI + '47m'

        assert str(bg.lightblack)   ==  CSI + '100m'
        assert str(bg.lightred)     ==  CSI + '101m'
        assert str(bg.lightgreen)   ==  CSI + '102m'
        assert str(bg.lightyellow)  ==  CSI + '103m'
        assert str(bg.lightblue)    ==  CSI + '104m'
        assert str(bg.lightmagenta) ==  CSI + '105m'
        assert str(bg.lightcyan)    ==  CSI + '106m'
        assert str(bg.lightwhite)   ==  CSI + '107m'


    def test_fxbasic():

        assert str(fx.end)          ==  CSI + '0m'
        assert str(fx.bold)         ==  CSI + '1m'
        assert str(fx.dim)          ==  CSI + '2m'
        assert str(fx.italic)       ==  CSI + '3m'
        assert str(fx.underline)    ==  CSI + '4m'
        assert str(fx.slowblink)    ==  CSI + '5m'
        assert str(fx.fastblink)    ==  CSI + '6m'
        assert str(fx.reverse)      ==  CSI + '7m'
        assert str(fx.conceal)      ==  CSI + '8m'
        assert str(fx.hide)         ==  CSI + '8m'
        assert str(fx.crossed)      ==  CSI + '9m'
        assert str(fx.strike)       ==  CSI + '9m'
        assert str(fx.frame)        ==  CSI + '51m'
        assert str(fx.encircle)     ==  CSI + '52m'
        assert str(fx.overline)     ==  CSI + '53m'

    def test_basic_wrong_name():
        with pytest.raises(AttributeError):
            fg.KERBLOOWIE


# Extended palette - fg.i
# ----------------------------------------------------------------------------
if True:  # fold

    def test_fgext_too_short():
        with pytest.raises(AttributeError) as err:
            fg.i
        assert 'length' in err.value.args[0]

    def test_fgext_one_digit():

        assert str(fg.i1) ==  CSI + '38;5;1m'

    def test_fgext_two_digit():

        assert str(fg.i11) == CSI + '38;5;11m'

    def test_fgext_three_digits():

        assert str(fg.i111) == CSI + '38;5;111m'

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

        assert str(bg.i1) ==  CSI + '48;5;1m'

    def test_bgext_two_digit():

        assert str(bg.i11) == CSI + '48;5;11m'

    def test_bgext_three_digits():

        assert str(bg.i111) == CSI + '48;5;111m'

    def test_bgext_too_long():
        with pytest.raises(AttributeError) as err:
            bg.i1111
        assert 'length' in err.value.args[0]


# Extended palette - fg.n - nearest
# ----------------------------------------------------------------------------
if True:  # fold

    def test_fgextn_too_short():
        with pytest.raises(AttributeError) as err:
            fg.n
        assert 'length' in err.value.args[0]

    def test_fgextn_three_digits():

        assert str(fg.nf0f) == CSI + '38;5;13m'

    def test_fgextn_four_digits():
        with pytest.raises(AttributeError) as err:
            fg.n1111
        assert 'length' in err.value.args[0]

    # bg
    def test_bgextn_one_digit():
        with pytest.raises(AttributeError) as err:
            bg.n1
        assert 'length' in err.value.args[0]

    def test_bgextn_three_digits():

        assert str(bg.n080) == CSI + '48;5;28m'

    def test_bgextn_too_long():
        with pytest.raises(AttributeError) as err:
            bg.nffff
        assert 'length' in err.value.args[0]


# True color palette - fg
# ----------------------------------------------------------------------------
if True:  # fold

    def test_fgtrue_too_short():
        with pytest.raises(AttributeError) as err:
            fg.tbb00
        assert 'length' in err.value.args[0]

    def test_fgtrue_three_digits():

        assert str(fg.tb0b) ==  CSI + '38;2;187;0;187m'

    def test_fgtrue_six_digits():

        assert str(fg.tff00bb) ==  CSI + '38;2;255;0;187m'

    def test_fgtrue_wrong_format():
        with pytest.raises(AttributeError) as err:
            fg.tbob
        assert 'hex digits' in err.value.args[0]

    def test_fgtrue_too_long():
        with pytest.raises(AttributeError) as err:
            fg.tDEADBEEFCAFE
        assert 'length' in err.value.args[0]

    # bg
    def test_bgtrue_too_short():
        with pytest.raises(AttributeError) as err:
            bg.tbb00
        assert 'length' in err.value.args[0]

    def test_bgtrue_three_digits():

        assert str(bg.tb0b) ==  CSI + '48;2;187;0;187m'

    def test_bgtrue_six_digits():

        assert str(bg.tff00bb) ==  CSI + '48;2;255;0;187m'

    def test_bgtrue_wrong_format():
        with pytest.raises(AttributeError) as err:
            bg.tbob
        assert 'hex digits' in err.value.args[0]

    def test_bgtrue_too_long():
        with pytest.raises(AttributeError) as err:
            bg.tDEADBEEFCAFE
        assert 'length' in err.value.args[0]


# Concat + str
# ----------------------------------------------------------------------------
if True:  # fold

    def test_string_concat_fg():
        text = fg.red + 'RED ' + fg.green + 'GRN ' + fg.blue + 'BLU' + fg.default
        assert text == CSI + '31mRED \x1b[32mGRN \x1b[34mBLU\x1b[39m'

    def test_string_concat_bg():
        text = bg.yellow + 'YEL ' + bg.magenta + 'MAG ' + bg.cyan + 'CYN' + bg.default
        assert text == CSI + '43mYEL \x1b[45mMAG \x1b[46mCYN\x1b[49m'

    def test_string_concat_fx():
        text = fx.bold + 'BLD ' + fx.underline + 'UND ' + fx.reverse + 'REV' + fx.end
        assert text == CSI + '1mBLD \x1b[4mUND \x1b[7mREV\x1b[0m'


# Concat + objects
# ----------------------------------------------------------------------------
if True:  # fold
        #~ print(f'{text!r} → {text}')

    def test_attribute_multiple_addition_no_accumulation():
        # make style with addition
        muy_importante = fg.white + fx.bold + bg.red
        # use
        text = muy_importante + ' ARRIBA! ' + fx.end
        assert text == CSI + '37;1;41m ARRIBA! \x1b[0m'

        # important check:
        # fg.white should not be affected, since we returned a new obj on add
        text = fg.white + 'FOO' + fx.end
        assert text == CSI + '37mFOO\x1b[0m'


# Call
# ----------------------------------------------------------------------------
if True:  # fold

    def test_attribute_call():
        text = bg.purple('⛈ PURPLE RAIN ⛈')

        assert text == CSI + '45m⛈ PURPLE\xa0RAIN ⛈\x1b[49m'
        # does better check now:
        #~ assert text == CSI + '45m⛈ PURPLE\xa0RAIN ⛈\x1b[0m'

    def test_attribute_call_plus_styles():
        linkstyle = fg.blue + fx.underline
        text = linkstyle('http://expertsexchange.com/', fx.blink)
        assert text == CSI + '34;4;5mhttp://expertsexchange.com/\x1b[0m'

# todo: problem
    def test_attribute_call_plus_styles2():
        # make style with addition
        muy_importante = fg.white + fx.bold + bg.red
        text = muy_importante('ARRIBA!')
        assert text == CSI + '37;1;41mARRIBA!\x1b[0m'


