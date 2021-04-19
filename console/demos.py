# -*- coding: future_fstrings -*-
'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    Demos showing what the library and terminal combo can do.
'''

# try some stuff out
def build_demos(caption, obj, extra_style=''):
    ''' Iterate over a Palette container and collect the items to add to
        demos.
    '''
    items = []
    for name in dir(obj):
        if not name.startswith('_') and not name == 'clear':  # types !work
            attr = getattr(obj, name)
            if extra_style:
                items.append(f'{attr + extra_style}{attr.name}{fx.end}')
            else:
                items.append(f'{attr}{attr.name}{fx.end}')
    return caption + ' '.join(items)


# util functions
def make_header(i):
    return f'  {fx.dim}{i+1:02d}{fx.end} '


def run():
    ''' Run the demos. '''
    import time

    print('\nConsole - ANSI lib demos, here we go:\n')
    hello_world = f'''Greetings: {fx.bold + fg.blue}Hello {fx.reverse +
                    fg.yellow}World{fg.default + defx.reverse}!{fx.end}'''
    # styles
    bad_grammar = fx.curly_underline + ul.i2
    bad_spelling = fx.curly_underline + ul.i1

    demos = [
        hello_world,
        f'↑ Title: {set_title("Console FTW! 🤣")!r} (gone in a µs.)',
        f'Combined, bold + underline + red: {fx.bold + fx.underline + fg.red}' +
            f'Merry {fg.green}X-Mas{fg.default}!{fx.end}',
        f'Cursor right → : [{sc.move_right}] (<-- one space between brackets)',
        f'Cursor down ↓ 2: {sc.move_down(2)}',

        'Text wrap: ' + fg.purple('Fill my eyes with that Double Vision…'
                            + BEL, fx.underline, fx.italic, fx.overline),

        'hyper-link: ' + make_hyperlink('http://www.coolsiteoftheday.com/',
                                        'Cool Site of the Day!'),
        'underline-hijinks: I %s %s' % (bad_grammar('not'), bad_spelling('mizpelled.')),
    ]

    if not _SHORT:
        demos.append(build_demos('FG:   ', fg))
        demos.append(build_demos('Bold: ', fg, extra_style=fx.bold))
        demos.append(build_demos('BG:   ', bg, extra_style=fg.black))
        demos.append(build_demos('FX:   ', fx))
        demos.append('Stripped: %r' % strip_ansi(hello_world))

    for i, demo in enumerate(demos):
        print(make_header(i), demo)
        if _DEBUG:
            log.debug('%r\n' % demo)

    if _SHORT:
        sys.exit()

    print()
    print(make_header(i+1), 'with bg:')
    msg = '\tCan I get the icon in Cornflower Blue?\n\tAbsolutely. :-D'
    try:
        with bg.cornflowerblue:
            print(msg)
    except AttributeError:
        with bg.blue:
            print(msg)
    print('\n')

    print(make_header(i+2), 'Foreground - 256 indexed colors:\n      ',
          end='')
    for j in range(256):
        attr = getattr(fg, f'i{j}')
        print(attr, '%4.4s' % attr.name.lower(), fx.end, end=' ')

        # newline every 16 columns :-/
        if not (j + 1) % 16:
            print('\n      ', end='')
    print()

    print(make_header(i+3), 'Background - 256 indexed colors:\n      ',
          end='')
    for j in range(256):

        attr = getattr(bg, f'i{j}')
        print(attr, '%4.4s' % attr.name.lower(), fx.end, end=' ')

        # NL every 16 columns :-/
        if not (j + 1) % 16:
            print('\n      ', end='')
    print()

    print(make_header(i+4), 'Foreground - Millions of colors: 24-bit:')
    print('      fg:', fg.tFF00BB, 'text_FF00BB', fx.end)
    print('      fg:', fg.tB0B,    'text_BOB', fx.end)
    print('      fg:', fg.tff00bb, 'text_FF00BB', fx.end)
    try:
        print('      fg:', fg.tFF00B, 'text_FF00B', fx.end)
    except AttributeError as err:
        print('      ', fg.red, fx.reverse, 'Error:', fx.end, ' ', err,
              '\n', sep='')

    print(make_header(i+5), 'Background - 24-bit, Millions of colors:')
    step = 3  # length of bar 256/3 = ~86

    # draw rounded box around gradients
    print('      ╭' + '─' * 86, '╮\n      │', sep='', end='')   # RED
    for val in range(0, 256, step):
        code = format(val, '02x')
        # probably don't need to end here every time:
        #~ print(getattr(bg, 't%s0000' % code), fx.end, end='')
        print(getattr(bg, 't%s0000' % code), end=' ')
    print(fx.end, '│', sep='')

    print('      │', sep='', end='')                            # GREEN
    for val in range(255, -1, -step):
        code = format(val, '02x')
        print(getattr(bg, 't00%s00' % code), fx.end, end='')
    print('│')

    print('      │', sep='', end='')                            # BLUE
    for val in range(0, 256, step):
        code = format(val, '02x')
        print(getattr(bg, 't0000%s' % code), fx.end, end='')
    print('│')
    print('      ╰' + '─' * 86, '╯\n', sep='', end='')
    print(flush=True)

    print(make_header(i+5), 'Progress Bars:')
    from console.progress import ProgressBar, HiDefProgressBar

    print()
    pb = ProgressBar(clear_left=False, label=True, width=36)
    print('    ', pb(0), end='')
    print('  ', pb(45), end='')
    print('  ', pb(99))
    print()

    pb = ProgressBar(clear_left=False, theme='solid', width=32)
    print('    ', pb(0), end='')
    print('      ', pb(55), end='')
    print('      ', pb(99))
    print()

    pb = HiDefProgressBar(clear_left=False, styles='greyen', width=36)
    print('    ', pb(0), end='')
    print('  ', pb(55), end='')
    print('  ', pb(99))
    print()

    print(make_header(i+5), 'Test color downgrade support '
                            '(True ⏵ Indexed ⏵ Basic):')
    try:
        import webcolors; webcolors # pyflakes
    except ImportError:
        print('      Test not available without webcolors installed.')
        sys.exit()

    if _term_level:
        bgall = style.BackgroundPalette(level=TermLevel.THE_FULL_MONTY);
        bge =   style.BackgroundPalette(level=TermLevel.ANSI_EXTENDED)
        bgb =   style.BackgroundPalette(level=TermLevel.ANSI_BASIC)
        print()

        colors = (
            't_222',            # grey
            't_808080',         # grey
            't_ccc',            # grey
            't_ddd',            # grey
            't_eee',            # grey
            't_e95420',         # ubuntu orange
            'coral',            # wc
            't_ff00ff',         # grey
            't_bb00bb',         # magenta
            'x_bisque',
            'x_dodgerblue',     # lighter blue
            'w_cornflowerblue', # lighter blue
            'w_navy',           # dark blue
            'w_forestgreen',    # dark/medium green
            'i_28',
            'i_160',
            'n_a08',
            'n_f0f',
            't_deadbf',
        )
        for i, color_key in enumerate(colors):
            full = getattr(bgall, color_key)
            dwne = getattr(bge, color_key)
            dwnb = getattr(bgb, color_key)

            print('      ', '%-18.18s' % (color_key + ':'),
                  full, ' t   ', fx.end, # bgall.default
                  dwne, ' i   ', fx.end, # broken on windows, mac terminal
                  dwnb, ' b   ', fx.end,
            sep='', end=' ')
            if i % 2 == 1:
                print()

        fgall = style.ForegroundPalette(level=TermLevel.THE_FULL_MONTY);
        fge =   style.ForegroundPalette(level=TermLevel.ANSI_EXTENDED)
        fgb =   style.ForegroundPalette(level=TermLevel.ANSI_BASIC)
        print('      FG t_deadbf:      ',
            fgall.t_deadbf('▉▉▉▉▉'),
            fge.t_deadbf('▉▉▉▉▉'),
            fgb.t_deadbf('▉▉▉▉▉'), fx.end,  # win bug
        sep='')
    else:
        print('      Term support not available.')
    print()

    if is_a_tty():
        try:
            print('       theme:', get_theme(timeout=1), '\n')
            print('       color scheme:', get_color('fg', timeout=1), 'on',
                                          get_color('bg', timeout=1), end='\n\n')
        except ModuleNotFoundError:
            pass  # termios - Windows

        try:
            print('       About to clear terminal, check title above. ☝  '
                  ' (Ctrl+C exits first.) ', end='', flush=True)
            time.sleep(10)     # wait to see terminal title
            cls()
        except KeyboardInterrupt:
            pass

    print()
    print()
    print('      ☛ Done, should be normal text. ☚  ')
    print()


if __name__ == '__main__':

    import sys, os
    import logging

    log = logging.getLogger(__name__)
    if os.name == 'nt':
        import env
        try:  # wuc must come before colorama.init() for detection to work.
            import win_unicode_console as wuc
            wuc.enable()
        except ImportError:
            pass
        try:
            if not env.ANSICON:
                import colorama
                colorama.init()  # is this run unnecessarily on newer Windows?
        except ImportError:
            pass

    # What needs to be done to get demos to run:
    _DEBUG = '-d' in sys.argv
    _SHORT = '-s' in sys.argv
    if _DEBUG:  # set up debug logging
        fmt = '  %(levelname)-7.7s %(module)s/%(funcName)s:%(lineno)s %(message)s'
        logging.basicConfig(level=logging.DEBUG, format=fmt)

    # detection already happened - need to run this again to log it. :-/
    from .detection import init
    from .detection import detect_unicode_support
    from . import style

    _using_terminfo = os.environ.get('PY_CONSOLE_USE_TERMINFO') == "1"
    _using_terminfo = bool(_using_terminfo or os.environ.get('SSH_CLIENT'))
    init(using_terminfo=_using_terminfo)

    detect_unicode_support()
    fg = style.ForegroundPalette()
    bg = style.BackgroundPalette()
    fx = style.EffectsPalette()
    ul = style.UnderlinePalette()
    defx = style.EffectsTerminator()

    from . import term_level as _term_level
    from .constants import BEL, TermLevel
    from .detection import is_a_tty, get_color, get_theme, is_fbterm
    from .screen import sc
    from .utils import set_title, strip_ansi, cls, make_hyperlink

    # curly, colored underlines not handled by linux consoles:
    if _term_level > TermLevel.ANSI_BASIC and not is_fbterm:
        from .style import ul
    else:
        fx.curly_underline = fx.underline  # downgrade

    run()
