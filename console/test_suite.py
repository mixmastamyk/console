'''
    .. console - Comprehensive escape sequence utility library for terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    Testen-Sie, bitte.
'''
from io import StringIO
import pytest

from . import detection, screen, style, utils, _set_debug_mode

# configure our own - force all palettes on
args = dict(autodetect=False, palettes=('basic', 'extended', 'truecolor'))

fg = style.ForegroundPalette(**args)
bg = style.BackgroundPalette(**args)
fx = style.EffectsPalette(**args)
defx = style.EffectsTerminator(**args)
sc = screen.Screen(autodetect=False)

fg, bg, fx, pytest  # pyflakes

# beginning of tests
_set_debug_mode(True)
CSI = '\x1b['           # sanity check



# Basic palette - fg, bg, fx
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
        assert str(fx.b)            ==  CSI + '1m'
        assert str(fx.dim)          ==  CSI + '2m'
        assert str(fx.italic)       ==  CSI + '3m'
        assert str(fx.i)            ==  CSI + '3m'
        assert str(fx.underline)    ==  CSI + '4m'
        assert str(fx.u)            ==  CSI + '4m'
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


# Extended palette - fg.i_, bg.i_
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

        assert str(fg.i_111) == CSI + '38;5;111m'

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


# Extended palette - fg.n_, bg._ - nearest
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
            bg.n_1
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

        assert str(fg.t_ff00bb) ==  CSI + '38;2;255;0;187m'

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

    def test_attribute_multiple_shorthand():
        # create style with addition, use
        XTREME_STYLING = fx.b + fx.i + fx.u
        arg = ' COWABUNGA, DUDE!! '
        text = XTREME_STYLING + arg + fx.end
        assert text == '%s1;3;4m%s%s0m' % (CSI, arg, CSI)
        #~ assert text == f'{CSI}1;3;4m{arg}{CSI}0m'

    def test_attribute_multiple_addition_no_accumulation():
        ''' Verify addition does not affect left-most addend. '''
        # create style with addition, use
        muy_importante = fg.white + fx.bold + bg.red
        arg = ' ARRIBA! '
        text = muy_importante + arg + fx.end
        assert text == '%s37;1;41m%s%s0m' % (CSI, arg, CSI)
        #~ assert text == f'{CSI}37;1;41m{arg}{CSI}0m'

        # important check:
        # fg.white should not be affected, since we returned a new copy on add
        text = fg.white + 'FOO' + fx.end
        assert text == CSI + '37mFOO\x1b[0m'

# Call
# ----------------------------------------------------------------------------
if True:  # fold

    def test_attribute_call():
        text = bg.purple('⛈ PURPLE RAIN ⛈')
        assert text == '\x1b[45m⛈ PURPLE\xa0RAIN ⛈\x1b[49m'

    def test_attribute_call_plus_styles():
        linkstyle = fg.blue + fx.underline
        text = linkstyle('http://expertsexchange.com/', fx.blink)
        assert text == '\x1b[34;4;5mhttp://expertsexchange.com/\x1b[0m'

    def test_attribute_call_plus_styles2():
        ''' Call style with mix-in. '''
        muy_importante = fg.white + fx.b + bg.red
        arg = ' ARRIBA! '
        text = muy_importante(arg, fx.u)
        assert text == '%s37;1;41;4m%s%s0m' % (CSI, arg, CSI)


# Screen
# ----------------------------------------------------------------------------
if True:  # fold

    def test_screen_eraseline():
        text = sc.eraseline(1)
        assert text == CSI + '1K'

    def test_screen_pos():
        text = sc.mv(20, 11)  # y, x
        assert text == CSI + '20;11H'

    def test_screen_save_restore():
        text = sc.save
        assert repr(text) == "'\\x1b[?47h'"

        text = sc.restore
        assert repr(text) == "'\\x1b[?47l'"

    def test_screen_save_restore_pos():
        text = sc.savepos
        assert repr(text) == "'\\x1b[s'"

        text = sc.restpos
        assert repr(text) == "'\\x1b[u'"

    def test_screen_reset():
        text = sc.reset
        assert repr(text) == "'\\x1bc'"

    def test_screen_bp_enable():
        bpon = "'\\x1b[?2004h'"
        bpoff = "'\\x1b[?2004l'"

        text = sc.bracketedpaste_enable
        assert repr(text) == bpon

        text = sc.bpon
        assert repr(text) == bpon

        text = sc.bracketedpaste_disable
        assert repr(text) == bpoff

        text = sc.bpoff
        assert repr(text) == bpoff

    def test_screen_cursor():
        for val in (2,3,5):
            for name in ('up', 'down', 'left', 'right'):
                attr = getattr(sc, name)
                text = attr(val)
                assert repr(text) == "'\\x1b[%s%s'" % (val, attr.code)


# Utils
# ----------------------------------------------------------------------------
if True:  # fold

    def test_utiles_clear_line():
        utils.screen = sc
        end = 'K'
        for i in range(3):
            text = utils.clear_line(i)
            assert text == CSI + str(i) + end

        for i, mode in enumerate(('forward', 'backward', 'full', 'history')):
            text = utils.clear_line(mode)
            assert text == CSI + str(i) + end

    def test_utiles_clear_screen():
        end = 'J'
        for i in range(3):
            text = utils.clear_screen(i)
            assert text == CSI + str(i) + end

        for i, mode in enumerate(('forward', 'backward', 'full', 'history')):
            text = utils.clear_screen(mode)
            assert text == CSI + str(i) + end

    def test_strip_ansi():
        text = 'Hang \x1b[34;4;5mLoose\x1b[0m, Hawaii'
        assert 'Hang Loose, Hawaii' == utils.strip_ansi(text)

    def test_strip_ansi_osc():
        text = '\x1b]0;Le Freak\x07, C\'est chic.'
        assert "Le Freak, C'est chic." == utils.strip_ansi(text, osc=True)

    def test_strip_ansi_len():
        text = 'Hang \x1b[34;4;5mLoose\x1b[0m, Hawaii'
        assert utils.len_stripped(text) == 18

    # TODO:
    # set_title
    # wait_key
    # pause


# Detection
# ----------------------------------------------------------------------------
if True:  # fold
    from env import Environment

    def test_color_disabled_none():
        detection.env = Environment(environ={})
        assert detection.color_is_disabled() == None

        detection.env = Environment(environ=dict(CLICOLOR=''))
        assert detection.color_is_disabled() == None

        detection.env = Environment(environ=dict(CLICOLOR='1'))
        assert detection.color_is_disabled() == None

    def test_color_disabled_true():
        detection.env = Environment(environ=dict(NO_COLOR='1'))
        assert detection.color_is_disabled() == True

        detection.env = Environment(environ=dict(CLICOLOR='0'))
        assert detection.color_is_disabled() == True

    def test_color_allowed():
        detection.env = Environment(environ={})
        assert detection.color_is_allowed() == True

        detection.env = Environment(environ=dict(CLICOLOR='0'))
        assert detection.color_is_allowed() == False

        detection.env = Environment(environ=dict(NO_COLOR=''))
        assert detection.color_is_allowed() == False

    def test_color_forced():
        detection.env = Environment(environ={})
        assert detection.color_is_forced() == None

        detection.env = Environment(environ=dict(CLICOLOR_FORCE='0'))
        assert detection.color_is_forced() == False

        detection.env = Environment(environ=dict(CLICOLOR_FORCE='foo'))
        assert detection.color_is_forced() == True

        detection.env = Environment(environ=dict(CLICOLOR_FORCE='1'))
        assert detection.color_is_forced() == True

    def test_palette_support():
        terms = (
            ('dumb', None),
            ('linux', 'basic'),
            ('xterm-color', 'basic'),
            ('xterm-256color', 'extended'),
            # ?
        )
        for name, result in terms:
            detection.env = Environment(environ=dict(TERM=name))
            assert detection.detect_palette_support() == result

        detection.env = Environment(environ=dict(ANSICON='1'))
        assert detection.detect_palette_support() == 'extended'

        detection.env = Environment(environ=dict(COLORTERM='24bit'))
        assert detection.detect_palette_support() == 'truecolor'

    def test_is_a_tty():
        f = StringIO()
        class YesMan:
            def isatty(self):
                return True

        assert detection.is_a_tty(outfile=None) == None
        assert detection.is_a_tty(outfile=f) == False
        assert detection.is_a_tty(outfile=YesMan()) == True

    def test_choose_palette():
        pass # TODO

    # not sure we can test term query functions, need to be more testable :-/
    def test_get_term_color():
        #~ assert detection.query_terminal_color('bg') == []
        pass  # gets correct results on osx ['ffff', 'ffff', 'ffff']

    def test_get_cursor_pos():
        #~ assert detection.get_cursor_pos() == ()
        pass  # gets correct results on osx (81, 40)


# Misc
# ----------------------------------------------------------------------------
if True:  # fold
    def test_context_mgr():
        try:
            import webcolors; webcolors # pyflakes

            f = StringIO()
            forestgreen = bg.wforestgreen + fx.bold
            forestgreen.set_output(f)
            with forestgreen:
                print('Testing, testing…', file=f)
                print('1, 2, 3.', file=f)

            result = '\x1b[48;2;34;139;34;1mTesting, testing…\n1, 2, 3.\n\x1b[0m'
            assert result == f.getvalue()

        except ImportError:
            pass  # not able to test

    def test_find_nearest_color_index():
        from .proximity import find_nearest_color_index
        values = (
            (0, 0, 0, 0),
            (16, 16, 16, 233),
            (256, 0, 0, 9),
            (0, 256, 0, 10),
            (176, 0, 176, 127),
            (256, 256, 256, 15),
        )
        for val in values:
            assert find_nearest_color_index(*val[:3]) == val[3]

    def test_find_nearest_color_hexstr():
        from .proximity import find_nearest_color_hexstr
        # test hex strings
        values = (
            ('000',   0),
            ('111', 233),  # grayscale
            ('222', 235),
            ('333', 236),
            ('444', 238),
            ('555', 240),
            ('666', 241),
            ('777', 243),
            ('888', 102),
            ('999', 246),
            ('aaa', 248),
            ('bbb', 250),
            ('ccc', 252),
            ('ddd', 253),
            ('eee',   7),
            ('fff',  15),

            ('f00',   9),
            ('0f0',  10),
            ('b0b', 127),
        )
        for val in values:
            assert find_nearest_color_hexstr(val[0]) == val[1]

