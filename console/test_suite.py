# -*- coding: future_fstrings -*-
'''
    .. console - Comprehensive ANSI sequence utility library for terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    Testen-Sie, bitte.  Supported under Linux with a libvte terminal.
'''
from io import StringIO, UnsupportedOperation

import pytest
try:
    import webcolors
except Exception:
    webcolors = None

from . import detection, screen, style, utils

from . import proximity, color_tables
from .constants import TermLevel
proximity.build_color_tables(base=color_tables.xterm_palette4)

# configure our own - force all palettes on
fg = style.ForegroundPalette(color_sep=';', level=TermLevel.THE_FULL_MONTY)
bg = style.BackgroundPalette(color_sep=':', level=TermLevel.THE_FULL_MONTY)
fx = style.EffectsPalette(level=TermLevel.THE_FULL_MONTY)
ul = style.UnderlinePalette(level=TermLevel.THE_FULL_MONTY)
defx = style.EffectsTerminator(level=TermLevel.THE_FULL_MONTY)
sc = screen.Screen(force=True)
scs = screen.Screen(force=True, swap=False)
utils._ansi_capable = True

fg, bg, fx, defx, ul, pytest  # pyflakes

# beginning of tests
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
        assert str(fx.dunder)       ==  CSI + '21m'
        assert str(fx.double_underline) ==  CSI + '21m'
        assert str(fx.curly_underline) ==  CSI + '4:3m'

    def test_debasic():
        dx = defx
        assert str(dx.end)          ==  CSI + '0m'
        assert str(dx.bold)         ==  CSI + '22m'
        assert str(dx.b)            ==  CSI + '22m'
        assert str(dx.dim)          ==  CSI + '22m'
        assert str(dx.italic)       ==  CSI + '23m'
        assert str(dx.i)            ==  CSI + '23m'
        assert str(dx.underline)    ==  CSI + '24m'
        assert str(dx.u)            ==  CSI + '24m'
        assert str(dx.reverse)      ==  CSI + '27m'
        assert str(dx.conceal)      ==  CSI + '28m'
        assert str(dx.hide)         ==  CSI + '28m'
        assert str(dx.crossed)      ==  CSI + '29m'
        assert str(dx.strike)       ==  CSI + '29m'
        assert str(dx.frame)        ==  CSI + '54m'
        assert str(dx.encircle)     ==  CSI + '54m'
        assert str(dx.overline)     ==  CSI + '55m'

    def test_ulbasic():
        assert str(ul.red)          ==  CSI + '58:2::255:0:0m'
        assert str(ul.i3)           ==  CSI + '58:5:3m'
        assert str(ul.t_123)        ==  CSI + '58:2::17:34:51m'
        assert str(ul.bisque)       ==  CSI + '58:2::255:228:196m'

    def test_basic_wrong_name():
        with pytest.raises(AttributeError):
            fg.KERBLOOWIE


# Extended palette - fg.i_, bg.i_
# ----------------------------------------------------------------------------
if True:  # fold

    def test_fgext_too_short():
        with pytest.raises(AttributeError) as err:
            fg.i
        assert 'recognized' in err.value.args[0]

    def test_fgext_one_digit():

        assert str(fg.i1) ==  CSI + '38;5;1m'

    def test_fgext_two_digit():

        assert str(fg.i11) == CSI + '38;5;11m'

    def test_fgext_three_digits():

        assert str(fg.i_111) == CSI + '38;5;111m'

    def test_fgext_four_digits():
        with pytest.raises(AttributeError) as err:
            fg.i1111
        assert 'recognized' in err.value.args[0]

    # bg
    def test_bgext_too_short():
        with pytest.raises(AttributeError) as err:
            bg.i
        assert 'recognized' in err.value.args[0]

    def test_bgext_one_digit():

        assert str(bg.i1) ==  CSI + '48:5:1m'

    def test_bgext_two_digit():

        assert str(bg.i11) == CSI + '48:5:11m'

    def test_bgext_three_digits():

        assert str(bg.i111) == CSI + '48:5:111m'

    def test_bgext_too_long():
        with pytest.raises(AttributeError) as err:
            bg.i1111
        assert 'recognized' in err.value.args[0]


# Extended palette - fg.n_, bg._ - nearest
# ----------------------------------------------------------------------------
if True:  # fold

    def test_fgextn_too_short():
        with pytest.raises(AttributeError) as err:
            fg.n
        assert 'recognized' in err.value.args[0]

    def test_fgextn_three_digits():

        assert str(fg.nf0f) == CSI + '38;5;13m'

    def test_fgextn_four_digits():
        with pytest.raises(AttributeError) as err:
            fg.n1111
        assert 'recognized' in err.value.args[0]

    # bg
    def test_bgextn_one_digit():
        with pytest.raises(AttributeError) as err:
            bg.n_1
        assert 'recognized' in err.value.args[0]

    def test_bgextn_three_digits():

        assert str(bg.n080) == CSI + '48:5:28m'

    def test_bgextn_too_long():
        with pytest.raises(AttributeError) as err:
            bg.nffff
        assert 'recognized' in err.value.args[0]


# True color palette - fg
# ----------------------------------------------------------------------------
if True:  # fold

    def test_fgtrue_too_short():
        with pytest.raises(AttributeError) as err:
            fg.tbb00
        assert 'recognized' in err.value.args[0]

    def test_fgtrue_three_digits():

        assert str(fg.tb0b) ==  CSI + '38;2;187;0;187m'

    def test_fgtrue_six_digits():

        assert str(fg.t_ff00bb) ==  CSI + '38;2;255;0;187m'

    def test_fgtrue_wrong_format():
        with pytest.raises(AttributeError) as err:
            fg.tbob
        assert 'recognized' in err.value.args[0]

    def test_fgtrue_too_long():
        with pytest.raises(AttributeError) as err:
            fg.tDEADBEEFCAFE
        assert 'recognized' in err.value.args[0]

    # bg
    def test_bgtrue_too_short():
        with pytest.raises(AttributeError) as err:
            bg.tbb00
        assert 'recognized' in err.value.args[0]

    def test_bgtrue_three_digits():

        assert str(bg.tb0b) ==  CSI + '48:2::187:0:187m'

    def test_bgtrue_six_digits():

        assert str(bg.tff00bb) ==  CSI + '48:2::255:0:187m'

    def test_bgtrue_wrong_format():
        with pytest.raises(AttributeError) as err:
            bg.tbob
        assert 'recognized' in err.value.args[0]

    def test_bgtrue_too_long():
        with pytest.raises(AttributeError) as err:
            bg.tDEADBEEFCAFE
        assert 'recognized' in err.value.args[0]


# Web color palette
# ----------------------------------------------------------------------------
if True:  # fold

    def test_webcolors_bisque():
        if webcolors:
            assert str(fg.bisque) == CSI + '38;2;255;228;196m'
            assert str(bg.w_bisque) == CSI + '48:2::255:228:196m'

    def test_webcolors_xyzzyx():
        if webcolors:
            with pytest.raises(AttributeError):  # as err:
            #~ assert 'recognized' in err.value.args[0]
                bg.w_xyzzyx


# X11 color palette
# ----------------------------------------------------------------------------
#~ if True:  # fold


# Concat + str
# ----------------------------------------------------------------------------
if True:  # fold

    def test_string_concat_fg():
        text = fg.red + 'RED ' + fg.green + 'GRN ' + fg.blue + 'BLU' + fg.default
        assert text == f'{CSI}31mRED {CSI}32mGRN {CSI}34mBLU{CSI}39m'

    def test_string_concat_bg():
        text = bg.yellow + 'YEL ' + bg.magenta + 'MAG ' + bg.cyan + 'CYN' + bg.default
        assert text == f'{CSI}43mYEL {CSI}45mMAG {CSI}46mCYN{CSI}49m'

    def test_string_concat_fx():
        text = fx.bold + 'BLD ' + fx.underline + 'UND ' + fx.reverse + 'REV' + fx.end
        assert text == f'{CSI}1mBLD {CSI}4mUND {CSI}7mREV{CSI}0m'


# Concat + objects
# ----------------------------------------------------------------------------
if True:  # fold
        #~ print(f'{text!r} → {text}')

    def test_attribute_multiple_shorthand():
        # create style with addition, use
        XTREME_STYLING = fx.b + fx.i + fx.u
        msg = ' COWABUNGA, DUDE!! '
        text = XTREME_STYLING + msg + fx.end
        assert text == f'{CSI}1;3;4m{msg}{CSI}0m'

    def test_attribute_multiple_addition_no_accumulation():
        ''' Verify addition does not affect left-most addend. '''
        # create style with addition, use
        muy_importante = fg.white + fx.bold + bg.red
        msg = ' ARRIBA! '
        text = muy_importante + msg + fx.end
        assert text == f'{CSI}37;1;41m{msg}{CSI}0m'

        # important check:
        # fg.white should not be affected, since we returned a new copy on add
        text = fg.white + msg + fx.end
        assert text == f'{CSI}37m{msg}{CSI}0m'

# Call
# ----------------------------------------------------------------------------
if True:  # fold

    def test_attribute_call():
        text = bg.purple('⛈ PURPLE RAIN ⛈')
        assert text == f'{CSI}45m⛈ PURPLE\xa0RAIN ⛈{CSI}49m'

    def test_attribute_call_plus_styles():
        linkstyle = fg.blue + fx.underline
        msg = 'http://expertsexchange.com/'
        text = linkstyle(msg, fx.blink)
        assert text == f'{CSI}34;4;5m{msg}{CSI}0m'

    def test_attribute_call_plus_styles2():
        ''' Call style with mix-in. '''
        muy_importante = fg.white + fx.b + bg.red
        msg = ' ARRIBA! '
        text = muy_importante(msg, fx.u)
        assert text == f'{CSI}37;1;41;4m{msg}{CSI}0m'

# Screen
# ----------------------------------------------------------------------------
if True:  # fold

    # ** repr's below prevent interpretation of sequences **
    def test_screen_clearline():
        assert sc.clear_line(1) == CSI + '1K'

    def test_screen_pos_std():
        assert sc.move_to(10, 20) == CSI + '21;11H'  # x, y  ->  y, x

    def test_screen_pos_swapped():
        assert scs.move_to(10, 20) == CSI + '11;21H'

    def test_screen_save_restore():
        assert repr(sc.enable_alt_screen) == "'\\x1b[?1049h'"
        assert repr(sc.disable_alt_screen) == "'\\x1b[?1049l'"

    def test_screen_save_restore_pos():
        assert repr(sc.save_position) == "'\\x1b7'"
        assert repr(sc.restore_position) == "'\\x1b8'"

    def test_screen_reset():
        assert repr(sc.reset) == "'\\x1bc'"

    def test_screen_bp_enable():
        bpon = "'\\x1b[?2004h'"
        bpoff = "'\\x1b[?2004l'"

        text = sc.enable_bracketed_paste
        assert repr(text) == bpon

        text = sc.disable_bracketed_paste
        assert repr(text) == bpoff

    def test_reverse_screen():
        assert sc.enable_flash == '\x1b[?5h'
        assert sc.disable_flash == '\x1b[?5l'

    def test_screen_cursor():
        for val in (2,3,5):
            for name in ('up', 'down', 'left', 'right'):
                attr = getattr(sc, 'move_' + name)
                text = attr(val)
                assert repr(text) == "'\\x1b[%s%s'" % (val, attr.endcode)


# Utils
# ----------------------------------------------------------------------------
if True:  # fold
    txt = ('\x1b[30m-C0-TEXT-\x1b[0m | \x9b30m-C1-Text-\x9bm | '
           '\x1b]L-OSC-C0-\x1b\\ | \x1b]L-OSC-C0-7-\a | \x9bL-OSC-C1-\x9d END')

    def test_utils_mk_hyperlink():
        utils._ansi_capable = True  # force for make
        result = utils.make_hyperlink('ftp://netscape.com/…/navigator.tar.gz',
                                      'Blast from the past!')
        assert result == (
            '\x1b]8;;ftp://netscape.com/%E2%80%A6/navigator.tar.gz'
            '\x1b\\Blast from the past!\x1b]8;;\x1b\\'
        )

    def test_utils_mk_hyperlink_params_and_low_encode():
        result = utils.make_hyperlink('foo://n\x1bt.org/', 'cap', id='2',
                                      bar='z', icon='')

        assert result == (
            '\x1b]8;id=2:bar=z;foo://n%1Bt.org/\x1b\\cap\x1b]8;;\x1b\\'
        )

    def test_utils_mk_hyperlink_bad_params():
        for char in (':', ';', '='):
            with pytest.raises(ValueError):
                utils.make_hyperlink('abc', 'xyz', foo='b%sar' % char)

    def test_utils_clear_line():
        utils.sc = sc
        end = 'K'
        for i in range(3):
            text = utils.clear_line(i)
            assert text == CSI + str(i) + end

        for i, mode in enumerate(('forward', 'backward', 'full', 'history')):
            text = utils.clear_line(mode)
            assert text == CSI + str(i) + end

    def test_utils_clear_lines():
        utils.sc = sc
        result = utils.clear_lines(3)
                          # 1A   1B     # 2A   2B     # 3A   3B
        assert result == '\x1b[2K\x1b[1A\x1b[2K\x1b[1A\x1b[2K\x1b[1A'

    def test_utils_clear_screen():
        utils.sc = sc
        end = 'J'
        for i in range(3):
            text = utils.clear_screen(i)
            assert text == CSI + str(i) + end

        for i, mode in enumerate(('forward', 'backward', 'full', 'history')):
            text = utils.clear_screen(mode)
            assert text == CSI + str(i) + end

    #~ def test_notify_progress():  # only on windows
        #~ cases = (
            #~ (-1, '\x1b]9;4;2;99\x1b\\'),
            #~ (00, '\x1b]9;4;0;0\x1b\\'),
            #~ (50, '\x1b]9;4;1;50\x1b\\'),
            #~ (99, '\x1b]9;4;1;99\x1b\\'),
            #~ (100, '\x1b]9;4;0;0\x1b\\'),
            #~ (101, '\x1b]9;4;2;99\x1b\\'),
            #~ (200, '\x1b]9;4;2;99\x1b\\'),
        #~ )
        #~ for value, expected in cases:
            #~ text = utils.notify_progress(value)
            #~ assert text == expected

    def test_notify_message():
        cases = (
            ('hi', '\x1b]9;hi\x1b\\'),
        )
        for value, expected in cases:
            text = utils.notify_message(value)
            assert text == expected

    def test_strip_ansi():
        text = 'Hang \x1b[34;4;5mLoose\x1b[0m, Hawaii'
        assert 'Hang Loose, Hawaii' == utils.strip_ansi(text)

    def test_strip_ansi_osc():
        text = '\x1b]lLe Freak\x07, C\'est chic.'
        assert ", C'est chic." == utils.strip_ansi(text, osc=True)
        text = '\x1b]lLe Freak\x1b\\, C\'est chic.'
        assert ", C'est chic." == utils.strip_ansi(text, osc=True)

    def test_strip_ansi_c1():
        assert ('-C0-TEXT- | -C1-Text- | \x1b]L-OSC-C0-\x1b\\ | '
                '\x1b]L-OSC-C0-7-\x07 | -OSC-C1-\x9d END'
                == utils.strip_ansi(txt, c1=True))

    def test_strip_ansi_c1_osc():
        assert ('-C0-TEXT- | -C1-Text- |  |  | -OSC-C1-\x9d END'
                == utils.strip_ansi(txt, c1=True, osc=True))

    def test_strip_ansi_len():
        text = 'Hang \x1b[34;4;5mLoose\x1b[0m, Hawaii'
        assert utils.len_stripped(text) == 18

    def test_set_cwd():
        utils._ansi_capable = True  # force for make
        result = utils.notify_cwd('/foo/bar/baz')
        assert result == '\x1b]7;file%3A///foo/bar/baz\x1b\\'

    # set_title - read title doesn't work to verify
    def test_set_title():
        text = 'foo'
        result = utils.set_title(text)
        assert result == '\x1b]0;foo\x1b\\'

        # xterm, make, mate term, iterm2
        possible_results = (text, None, 'Terminal', '',
            # iterm2, sigh:
            text + ' (fish)', text + ' (bash)', text + ' (Python)'
        )
        # best effort test
        try:
            assert detection.get_title() in possible_results
        except UnsupportedOperation:
            pass

    def test_set_clipboard():
        data = 'collywobbles'
        result = utils.set_clipboard(data)
        # best effort test, may not be allowed to succeed:
        assert utils.get_clipboard() in (None, '', data)
        if result is not None:
            assert result == b'\x1b]52;c;Y29sbHl3b2JibGVz\x1b\\'

    def test_wait_pause():
        ''' weak test, make sure funcs exist. '''
        utils.wait_key
        utils.pause
        if not detection.is_a_tty():

            utils.wait_key()
            utils.pause('')


# Detection
# ----------------------------------------------------------------------------
if True:  # fold
    from env import Environment

    def test_color_disabled_none_false():
        detection.env = Environment(environ={})
        assert detection.color_is_disabled() is None

        detection.env = Environment(environ=dict(CLICOLOR=''))
        assert detection.color_is_disabled() is None

        detection.env = Environment(environ=dict(CLICOLOR='1'))
        assert detection.color_is_disabled() is False

    def test_color_disabled_true():
        detection.env = Environment(environ=dict(NO_COLOR='1'))
        assert detection.color_is_disabled() is True

        detection.env = Environment(environ=dict(CLICOLOR='0'))
        assert detection.color_is_disabled() is True

    def test_color_forced():
        detection.env = Environment(environ={})
        assert detection.color_is_forced().value is None

        detection.env = Environment(environ=dict(CLICOLOR_FORCE='0'))
        assert detection.color_is_forced() is False

        detection.env = Environment(environ=dict(CLICOLOR_FORCE='foo'))
        assert detection.color_is_forced() is True

        detection.env = Environment(environ=dict(CLICOLOR_FORCE='1'))
        assert detection.color_is_forced() is True

    def test_color_sep():

        assert str(bg.i_11) == CSI + '48:5:11m'  # sanity check
        _bg = style.BackgroundPalette(color_sep=';', level=TermLevel.THE_FULL_MONTY)
        assert str(_bg.i_123) == CSI + '48;5;123m'

        _fg = style.ForegroundPalette(color_sep='_', level=TermLevel.THE_FULL_MONTY)
        assert str(_fg.bisque) == CSI + '38_2_255_228_196m'

    def test_terminal_level_detection():
        terms = (
            ('dumb', (TermLevel.DUMB, ';')),
            ('linux', (TermLevel.ANSI_BASIC, ';')),
            ('xterm-color', (TermLevel.ANSI_BASIC, ';')),
            ('xterm-256color', (TermLevel.ANSI_EXTENDED, ';')),
            ('xterm-direct', (TermLevel.ANSI_DIRECT, ':')),
            ('fbterm', (TermLevel.ANSI_EXTENDED, ';')),
        )
        for name, expected in terms:
            detection.env = Environment(environ=dict(TERM=name))
            if name == 'fbterm':  # :-/
                detection.is_fbterm = True
            assert detection.detect_terminal_level() == expected

        detection.env = Environment(environ=dict(COLORTERM='24bit'))
        detection.is_fbterm = False  # :-/
        assert detection.detect_terminal_level() == (TermLevel.ANSI_DIRECT, ';')

        from . import windows  # try win implementation
        terms = (
            ('dumb', (TermLevel.DUMB, ';')),
            ('xterm-color', (TermLevel.ANSI_BASIC, ';')),
            ('xterm-256color', (TermLevel.ANSI_EXTENDED, ';')),
            ('cygwin', (TermLevel.ANSI_DIRECT, ';')),  # ?
        )
        for name, expected in terms:
            windows.env = Environment(environ=dict(TERM=name))
            assert windows.detect_terminal_level() == expected

        windows.env = Environment(environ=dict(ANSICON='1'))
        assert windows.detect_terminal_level() ==( TermLevel.ANSI_EXTENDED, ';')

    def test_terminal_level_detection_override():
        terms = (
            ('dumb', (TermLevel.DUMB, '@')),
            ('linux', (TermLevel.ANSI_BASIC, '@')),
            ('xterm-color', (TermLevel.ANSI_BASIC, '@')),
            ('xterm-256color', (TermLevel.ANSI_EXTENDED, '@')),
            ('xterm-direct', (TermLevel.ANSI_DIRECT, '@')),
            ('fbterm', (TermLevel.ANSI_EXTENDED, '@')),
        )
        for name, expected in terms:
            detection.env = Environment(environ=dict(TERM=name, PY_CONSOLE_COLOR_SEP='@'))
            if name == 'fbterm':  # :-/
                detection.is_fbterm = True
            assert detection.detect_terminal_level() == expected

        from . import windows  # try win implementation
        terms = (
            ('dumb', (TermLevel.DUMB, '@')),
            ('xterm-color', (TermLevel.ANSI_BASIC, '@')),
            ('xterm-256color', (TermLevel.ANSI_EXTENDED, '@')),
            ('cygwin', (TermLevel.ANSI_DIRECT, '@')),  # ?
        )
        for name, expected in terms:
            windows.env = Environment(environ=dict(TERM=name, PY_CONSOLE_COLOR_SEP='@'))
            assert windows.detect_terminal_level() == expected

        windows.env = Environment(environ=dict(ANSICON='1'))
        assert windows.detect_terminal_level() ==( TermLevel.ANSI_EXTENDED, ';')

    def test_find_basic_palette_by_term():
        ct = color_tables
        test_map = {  # TERM: expected name/palette
            'xterm':           ('xterm',  ct.xterm_palette4),
            'xterm-256color':  ('xterm',  ct.xterm_palette4),
            'xterm-direct':    ('xterm',  ct.xterm_palette4),
            'linux':           ('linux',  ct.linuxcon_palette4),
            'fbterm':          ('fbterm', ct.linuxcon_palette4),
            'iterm2':          ('iterm',  ct.iterm_palette4),
            'nsterm':          ('nsterm', ct.termapp_palette4),
            'kitty':           ('xterm',  ct.xterm_palette4),  # try less common
        }
        for TERM in test_map:
            pal_name, palette = detection._find_basic_palette_from_term(TERM)
            expected_name, expected_palette = test_map.get(
                TERM, ct.DEFAULT_BASIC_PALETTE
            )
            assert pal_name == expected_name
            assert palette is expected_palette

    def test_is_a_tty():
        f = StringIO()
        class YesMan:
            def isatty(self):
                return True

        assert detection.is_a_tty(stream=None) == None
        assert detection.is_a_tty(stream=f) == False
        assert detection.is_a_tty(stream=YesMan()) == True

    # not sure how we can test term-specific query functions:
    def test_get_term_color():
        detection.get_color('bg') #== []
        pass  # gets correct results on osx/iterm ['ffff', 'ffff', 'ffff']

    def test_get_cursor_pos():
        # gets correct results on osx/iterm (81, 40)
        # doesn't work under pytest under make
        try:
            result = detection.get_position()
            assert isinstance(result, tuple)
        except UnsupportedOperation:
            pass

# downgrade support:

    def test_downgrade():
        bgall = style.BackgroundPalette(color_sep=':', level=TermLevel.THE_FULL_MONTY)
        bge = style.BackgroundPalette(color_sep=':', level=TermLevel.ANSI_EXTENDED)
        bgb = style.BackgroundPalette(color_sep=':', level=TermLevel.ANSI_BASIC)
        E = CSI

        results = (
          ('t_222'           , E+'48:2::34:34:34m'   , E+'48:5:235m', E+'40m'),
          ('t_808080'        , E+'48:2::128:128:128m', E+'48:5:244m', E+'100m'),
          ('t_ccc'           , E+'48:2::204:204:204m', E+'48:5:252m', E+'47m'),
          ('t_ddd'           , E+'48:2::221:221:221m', E+'48:5:253m', E+'47m'),
          ('t_eee'           , E+'48:2::238:238:238m', E+'48:5:255m', E+'47m'),
          ('t_e95420'        , E+'48:2::233:84:32m'  , E+'48:5:166m', E+'101m'),
          ('coral'           , E+'48:2::255:127:80m' , E+'48:5:209m', E+'43m'),
          ('t_ff00ff'        , E+'48:2::255:0:255m'  , E+'48:5:13m' , E+'105m'),
          ('t_bb00bb'        , E+'48:2::187:0:187m'  , E+'48:5:127m', E+'45m'),
          ('x_bisque'        , E+'48:2::255:228:196m', E+'48:5:224m', E+'47m'),
          ('x_dodgerblue'    , E+'48:2::30:144:255m' , E+'48:5:33m' , E+'104m'),
          ('w_cornflowerblue', E+'48:2::100:149:237m', E+'48:5:69m' , E+'104m'),
          ('w_navy'          , E+'48:2::0:0:128m'    , E+'48:5:18m' , E+'44m'),
          ('w_forestgreen'   , E+'48:2::34:139:34m'  , E+'48:5:28m' , E+'42m'),
          ('i_28'            , E+'48:5:28m'          , E+'48:5:28m' , E+'42m'),
          ('i_160'           , E+'48:5:160m'         , E+'48:5:160m', E+'41m'),
          ('n_a08'           , E+'48:5:126m'         , E+'48:5:126m', E+'45m'),
          ('n_f0f'           , E+'48:5:13m'          , E+'48:5:13m' , E+'105m'),
        )

        for result in results:
            full = getattr(bgall, result[0])
            dwne = getattr(bge, result[0])
            dwnb = getattr(bgb, result[0])

            assert str(full) == result[1]
            assert str(dwne) == result[2]
            assert str(dwnb) == result[3]


# Misc
# ----------------------------------------------------------------------------
if True:  # fold

    def test_context_mgr():

        from .core import _LineWriter
        forestgreen = bg.green + fx.bold
        outf = _LineWriter(str(forestgreen), StringIO(), forestgreen.default)

        with forestgreen:
            print(' Testing, \n Testing… ', file=outf)
            print(' 1, 2, 3. ', file=outf)

        result = ('\x1b[42;1m Testing, \x1b[0m\n'
                  '\x1b[42;1m Testing… \x1b[0m\n'
                  '\x1b[42;1m 1, 2, 3. \x1b[0m\n')
        assert result == outf.getvalue()

    def test_find_nearest_color_index():
        from .proximity import find_nearest_color_index
        values = (
            (0, 0, 0, 0),       # r, g, b, index
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

        values = (
            ('000',   0),   # hex strings, index
            ('111', 233),   # grayscale
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
            ('eee', 255),
            ('fff',  15),

            ('f00',   9),
            ('0f0',  10),
            ('b0b', 127),
        )
        for val in values:
            assert find_nearest_color_hexstr(val[0]) == val[1]

    def test_compute_attr_created_once():
        ''' Attributes should only be created once. '''
        attrid1 = id(fg.t_ff00ff)
        attrid2 = id(fg.t_ff00ff)
        attrid3 = id(bg.red)
        attrid4 = id(bg.red)

        assert attrid1 == attrid2
        assert attrid3 == attrid4

    def test_style_plus_call_construct():
        ''' test warning on inefficient/problematic form '''
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")  # all warnings always
            # trigger
            fg.green + bg.red('Merry\nXmas!')
            # verify:
            assert len(w) == 1
            assert issubclass(w[-1].category, SyntaxWarning)
            assert "Ambiguous" in str(w[-1].message)

    def test_raise_on_call_default_defx():
        '''  Prevent calling on default or defx. '''
        with pytest.raises(NotImplementedError):
            fg.default('foo')

        with pytest.raises(NotImplementedError):
            defx.italic('foo')


# Progress
# ----------------------------------------------------------------------------
if True:  # fold
    import console  # need these to force progress bar output
    console.fg = fg
    console.fx = fx
    console.bg = bg
    console.sc = sc
    console.term_level = TermLevel.ANSI_EXTENDED  # patch for hicolor theme
    from console.progress import ProgressBar, HiDefProgressBar

    def test_progress_ascii():

        pb = ProgressBar(clear_left=False, theme='basic', width=36)
        assert str(pb(-7))  == '<------------------------------] ERR'
        assert str(pb(0))   == '[------------------------------]  0%'
        assert str(pb(55))  == '[#################-------------] 56%'
        assert str(pb(99))  == '[##############################]   +'
        assert str(pb(103)) == '[##############################> ERR'

    def test_progress_solid():

        pb = ProgressBar(theme='solid')
        assert str(pb(-2))  == '\r\x1b[91m⏴\x1b[39m\x1b[48:5:236m                              \x1b[49m\x1b[2;38;5;236m▏\x1b[0m'
        assert str(pb(0))   == '\r\x1b[2;38;5;70m▕\x1b[0m\x1b[48:5:236m               0%             \x1b[49m\x1b[2;38;5;236m▏\x1b[0m'
        assert str(pb(16))  == '\r\x1b[2;38;5;70m▕\x1b[0m\x1b[48:5:70;30m     \x1b[0m\x1b[48:5:236m         16%             \x1b[49m\x1b[2;38;5;236m▏\x1b[0m'
        assert str(pb(99))  == '\r\x1b[2;38;5;70m▕\x1b[0m\x1b[48:5:22m                ✓             \x1b[49m\x1b[2;38;5;70m▏\x1b[0m'
        assert str(pb(112)) == '\r\x1b[2;38;5;70m▕\x1b[0m\x1b[48:5:22m                              \x1b[49m\x1b[91m⏵\x1b[39m'

    def test_progress_solid_clear_4():

        pb = ProgressBar(theme='solid', clear_left=4)
        assert str(pb(-2))  == '\r\x1b[4G\x1b[91m⏴\x1b[39m\x1b[48:5:236m                              \x1b[49m\x1b[2;38;5;236m▏\x1b[0m'
        assert str(pb(0))   == '\r\x1b[4G\x1b[2;38;5;70m▕\x1b[0m\x1b[48:5:236m               0%             \x1b[49m\x1b[2;38;5;236m▏\x1b[0m'
        assert str(pb(16))  == '\r\x1b[4G\x1b[2;38;5;70m▕\x1b[0m\x1b[48:5:70;30m     \x1b[0m\x1b[48:5:236m         16%             \x1b[49m\x1b[2;38;5;236m▏\x1b[0m'
        assert str(pb(99))  == '\r\x1b[4G\x1b[2;38;5;70m▕\x1b[0m\x1b[48:5:22m                ✓             \x1b[49m\x1b[2;38;5;70m▏\x1b[0m'
        assert str(pb(112)) == '\r\x1b[4G\x1b[2;38;5;70m▕\x1b[0m\x1b[48:5:22m                              \x1b[49m\x1b[91m⏵\x1b[39m'

    def test_progress_hidef1():

        pb = HiDefProgressBar(clear_left=False, styles='greyen')

        assert str(pb(-2))  == '\x1b[91m⏴\x1b[39m\x1b[38;5;236m▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉\x1b[39m\x1b[2;38;5;236m▏\x1b[0m\x1b[91m  ✗ \x1b[39m'
        assert str(pb(0))   == '\x1b[2;32m▕\x1b[0m\x1b[38;5;236m▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉\x1b[39m\x1b[2;38;5;236m▏\x1b[0m  0%'
        assert str(pb(18.1))  == '\x1b[2;32m▕\x1b[0m\x1b[32m▉▉▉▉\x1b[39m\x1b[32;48:5:236m▊\x1b[0m\x1b[38;5;236m▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉\x1b[39m\x1b[2;38;5;236m▏\x1b[0m 18%'
        assert str(pb(99))  == '\x1b[2;32m▕\x1b[0m\x1b[2;32m▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉\x1b[0m\x1b[2;32m▏\x1b[0m   ✓'
        assert str(pb(111.9)) == '\x1b[2;32m▕\x1b[0m\x1b[2;32m▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉▉\x1b[0m\x1b[91m⏵\x1b[39m\x1b[91m  ✗ \x1b[39m'

# Line
# ----------------------------------------------------------------------------
if True:  # fold
    from .utils import make_line
    _def_width = 80

    def test_line_std():
        expected = f'\x1b[2m{"─" * _def_width}\x1b[22m'
        assert make_line() == expected

    def test_line_color():
        expected = f'\x1b[31m{"─" * _def_width}\x1b[39m'
        assert make_line(color='red') == expected

    def test_line_str():
        char = '='
        expected = f'\x1b[2m{char * _def_width}\x1b[22m'
        assert make_line(string=char) == expected

    def test_line_width():
        width = 10
        expected = f'\x1b[2m{"─" * width}\x1b[22m'
        assert make_line(width=width) == expected

    def test_line_center_no_widt():
        with pytest.raises(RuntimeError):
            make_line(center=True)

    # helpers
    _get_spacing = lambda columns, width: " " * ((columns - width) // 2)
    _ansi_chars = 9  # len('\x1b[2m\x1b[22m')

    def test_line_center_width_even():
        width = 10  # even, even
        spaces = _get_spacing(_def_width, width)
        expected = f'\x1b[2m{spaces}{"─" * width}{spaces}\x1b[22m'
        result = make_line(width=width, center=True)
        assert result == expected

    def test_line_center_columns_odd():
        width = 10  # even
        columns = 81  # odd
        spaces = _get_spacing(columns, width)
        expected = f'\x1b[2m{spaces}{"─" * width}{spaces} \x1b[22m' # 👀 space
        result = make_line(width=width, center=True, _fallback=columns)

        assert result == expected
        assert len(result) == columns + _ansi_chars

    def test_line_center_width_odd():
        width = 11  # odd
        columns = 80  # even
        spaces = _get_spacing(columns, width)
        expected = f'\x1b[2m{spaces}{"─" * width}{spaces} \x1b[22m' # 👀 SP
        result = make_line(width=width, center=True, _fallback=columns)

        assert result == expected
        assert len(result) == columns + _ansi_chars
