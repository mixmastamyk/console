# -*- coding: future_fstrings -*-
'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    Experimental Progress Bar functionality.

    A demo is available via command-line::

        ▶ python3 -m console.progress [-l] [-d]  # label and debug modes

    TODO:

        - Gradients/rainbar
        - Additional tests
'''
import logging
import time
from math import floor

from . import fg, bg, fx, sc, term_level as _term_level
from .constants import TermLevel
from .detection import detect_unicode_support, get_size, os_name
from .disabled import empty as _empty
from .utils import len_stripped, notify_progress

DEF_TOTAL = 99
DEF_WIDTH = 32
MIN_WIDTH = 12
TIMEDELTAS = (60, 300)  # accuracy thresholds, in seconds, one and five minutes
term_width = _term_width_orig = get_size()[0]
log = logging.getLogger(__name__)

# Theme-ing info:
icons = dict(
    # name:      first, complete, empty, last, done, err_lo, err_hi, err_lbl
    ascii       = ('[', '#', '-', ']', '+', '<', '>', 'ERR'),
    blocks      = (' ', '▮', '▯', ' ', '✓', '⏴', '⏵', '✗'),
    # empty white bullet is the wrong size, breaks alignment:
    boxes       = (' ', '▣', '□', ' ', '✓', '⏴', '⏵', '✗'),
    bullets     = (' ', '•', '•', ' ', '✓', '⏴', '⏵', '✗'),
    dies        = (' ', '⚅', '⚀', ' ', '✓', '⏴', '⏵', '✗'),
    horns       = ('🤘', '⛧', '⛤', '🤘', '✓', '⏴', '⏵', '✗'),
    segmented   = ('▕', '▉', '▉', '▏', '✓', '⏴', '⏵', '✗ '),
    faces       = (' ', '☻', '☹', ' ', '✓', '⏴', '⏵', '✗'),
    wide_faces  = (' ', '😎', '😞', ' ', '✓', '⏴', '⏵', '✗'),
    stars       = ('(', '★', '☆', ')', '✓', '⏴', '⏵', '✗'),
    shaded      = ('▕', '▓', '░', '▏', '✓', '⏴', '⏵', '✗'),
    triangles   = ('▕', '▶', '◁', '▏', '✓', '⏴', '⏵', '✗'),
    spaces      = ('▕', ' ', ' ', '▏', '✓', '⏴', '⏵', '✗'),
)

# icon/style indexes
# 0    1    2    3    4     5     6     7
_if, _ic, _ie, _il, _id, _iel, _ieh, _ieb = range(8)


# styles
_dim_green = fx.dim + fg.green
_dim_amber = fx.dim + fg.i208
_err_color = fg.lightred
styles = dict(
    dumb        = (_empty,) * 6,  # monochrome
    # basic, 16 colors or less
    simple      = ( # str no longer works, call broke fbterm, so using ''
                    str,                # first,
                    str,                # complete
                    fx.dim,             # empty
                    str,                # last
                    fx.dim,             # done
                    _err_color,         # error
                  ),
    ocean       = (
                    _dim_green,         # first
                    fg.green,           # complete
                    fg.blue,            # empty
                    fx.dim + fg.blue,   # last
                    _dim_green,         # done
                    _err_color,         # error
                  ),
    # eight-bit color or higher
    amber       = (
                    _dim_amber,   # first
                    fg.i208,            # complete
                    fg.i172,            # empty
                    fx.dim + fg.i172,   # last
                    fg.i172,            # done
                    _err_color,         # error
                  ),
    amber_mono  = (
                    fx.dim + fg.i208,   # first
                    fx.reverse + fg.i208, # complete
                    fg.i172,   # empty
                    fx.dim + fg.i172,   # last
                    fx.dim + fx.reverse + fg.i208,  # done
                    _err_color,         # error
                  ),
    reds        = (
                    fx.dim + fg.red,    # first
                    fg.lightred,        # complete
                    fg.i236,            # empty
                    fg.i236,            # last
                    fg.red,             # done
                    _err_color,         # error
                  ),
    greyen      = (
                    _dim_green,         # first
                    fg.green,           # complete
                    fg.i236,            # empty
                    fx.dim + fg.i236,   # last
                    _dim_green,         # done
                    _err_color,         # error
                  ),
    greyam       = (
                    _dim_amber,   # first
                    fg.i208,            # complete
                    fg.i236,            # empty
                    fx.dim + fg.i236,   # last
                    _dim_amber,         # done
                    _err_color,         # error
                  ),
    ocean8       = (
                    fx.dim + fg.i70,    # first
                    fg.i70,             # complete
                    fg.i24,             # empty
                    fx.dim + fg.i24,    # last
                    fx.dim + fg.i70,    # done
                    _err_color,         # error
                  ),
    greyen_bg   = (
                    _dim_green,         # first
                    bg.lightgreen + fg.black,  # complete
                    bg.lightblack,      # empty
                    fg.lightblack,      # last
                    bg.green,           # done
                    _err_color,         # error
                  ),
    greyen_bg8   = (
                    fx.dim + fg.i70,    # first
                    bg.i70 + fg.black,  # complete
                    bg.i236,            # empty
                    fx.dim + fg.i236,   # last
                    bg.i22,             # done
                    _err_color,         # error
                  ),
)

themes = dict(
    basic_color = dict(icons='ascii', styles='ocean'),
    basic = dict(icons='ascii', styles='dumb'),
    boxes = dict(icons='boxes', styles='default'),
    dies = dict(icons='dies', styles='simple',
                partial_chars='⚀⚁⚂⚃⚄⚅', partial_char_extra_style=fg.white),
    hd_amber = dict(icons='segmented', styles='greyam'),
    hd_green = dict(icons='segmented', styles='greyen'),
    heavy_metal = dict(icons='horns', styles='reds'),
    shaded = dict(icons='shaded', styles='ocean'),
    solid = dict(icons='spaces', styles='greyen_bg'),
    warm_shaded = dict(icons='shaded', styles='amber'),
)

# figure defaults, icons and styles
styles['default'] = styles['dumb']
icons['default']  = icons['ascii']
themes['default'] = dict(icons='default', styles='default')  # loaded later
_unicode_support = detect_unicode_support()

# U-P-G-R-A-Y-E-D-D, a double-dose of unicode and colors…
if _unicode_support:
    icons['default']  = icons['blocks']

if _term_level >= TermLevel.ANSI_BASIC:
    styles['default'] = styles['ocean']

if _term_level >= TermLevel.ANSI_EXTENDED:
    styles['default'] = styles['ocean8']
    themes['solid']['styles'] = 'greyen_bg8'   # upgrade to hi color


class ProgressBar:
    ''' A stylable bar graph for displaying the current progress of task
        completion.

        ProgressBar is 0-based, i.e. think 0-99 rather than 1-100
        The execution flows like this:

            - __init__()
            - bar() # __call__() by code to set parameters
                - _update_status()  # check errors and set progress label

            - __str__() # and when printed
                - render()

        Example::

            from time import sleep  # demo purposes only
            from console.screen import sc
            from console.progress import ProgressBar

            with sc.hidden_cursor():

                items = range(256)      # example tasks
                bar = ProgressBar(total=len(items))  # set total

                # simple loop
                for i in items:
                    print(bar(i), end='', flush=True)
                    sleep(.02)
                print()

                # with caption
                for i in items:
                    print(bar(i), f' copying: /path/to/img_{i:>04}.jpg',
                          end='', flush=True)
                    sleep(.1)
                print()

                # or use as a simple tqdm-style iterable wrapper:
                for i in ProgressBar(range(100)):
                    sleep(.1)

        Arguments:
            clear_left: True        True to clear and mv to 0, or int offset
            debug: None             Enable debug output
            done: False             True on completion, moderates style
            expand: False           Set width to full terminal width
            iterable: object        An object to iterate on.
            label_mode:  True       Enable progress percentage label
            oob_error:  False       Out of bounds error occurred
            total:  99              Set the total number of items
            unicode_support: bool   Detection result, determines default icons
            width: 32               Full width of bar, padding, and labels

            icons:  (,,,)           Tuple of chars
            styles: (,,,)           Tuple of ANSI styles
            theme: 'name'           String name of combined icon & style set

            label_fmt: ('%3.0f%%', '%4.1f%%', '%5.2f%%')
                Precision—defaults to no decimal places.  After each timedelta,
                label precision is increased.
            timedeltas:(60, 300) | None     Thresholds in seconds,
                                            to increase label precision
    '''
    debug = None
    done = False
    expand = False
    label_fmt = ('%3.0f%%', '%4.1f%%', '%5.2f%%')
    label_fmt_str = '%4s'
    label_mode = True
    oob_error = False
    timedeltas = TIMEDELTAS
    total = None
    unicode_support = _unicode_support
    width = DEF_WIDTH

    theme = 'default'
    icons = icons[theme]
    styles = styles[theme]

    _clear_left = True
    _cached_str = None
    _min_width = MIN_WIDTH
    _num_complete_chars = 0
    _remainder = 0
    _iter_n = 0

    def __init__(self, iterable=None, **kwargs):
        # configure instance
        for key, val in kwargs.items():
            if key == 'theme':
                self.icons = icons[themes[val]['icons']]
                self.styles = styles[themes[val]['styles']]
                if val.startswith('basic'):
                    self.unicode_support = False
                elif val == 'solid':
                    self.label_mode = 'internal'
            elif key == 'icons':
                self.icons = icons[val]
                if val == 'ascii':
                    self.unicode_support = False
            elif key == 'styles':
                self.styles = styles[val]
            elif key == 'expand' and val:
                self.width = term_width
                self.expand = val
                install_resize_handler()
            else:
                setattr(self, key, val)

        # figure widths
        _icons = self.icons
        if self.width < self._min_width:
            self.width = self._min_width
        self.padding = len(_icons[_if]) + len(_icons[_il])  # bookends
        self._bwidth = self._set_bar_width()
        if self._clear_left is True:
            self.clear_left = self._clear_left  # render

        # configure styles
        _styles = self.styles
        self._comp_style = _styles[_ic]
        self._empt_style = _styles[_ie]
        self._err_style = _styles[_iel]
        self._first = _styles[_if](_icons[_if])
        self._last = _styles[_il](_icons[_il])

        self.reset()  # start time  TODO: move to end

        # tqdm-style iterable interface
        if iterable and not self.total:
            try:
                self.total = len(iterable)
            except (TypeError, AttributeError):
                self.total = None
            self.iterable = iterable
            self(self._iter_n)  # call() with initial value of 0
        elif self.total is None:
            self.total = DEF_TOTAL

    def _set_bar_width(self, width=None):
        ''' Determine the width of the bar only, without labels. '''
        if not width:  # determine
            if self.expand:
                width = term_width
            else:
                width = self.width
        if width < self._min_width:
            width = self._min_width

        self._bwidth_base = width - self.padding
        return self._bwidth_base

    def __len__(self):
        return self.total

    def __iter__(self):
        ''' tqdm-style iterable interface: https://tqdm.github.io/ '''
        for obj in self.iterable:
            yield obj
            self._iter_n += 1
            self(self._iter_n)  # call complete
            print(self, end='')
        print()

    def __str__(self):
        ''' Renders the current state as a string. '''
        if self._cached_str:
            return self._cached_str

        # shall we clear the line to the left?
        pieces = [self._clear_left if self._clear_left else '']

        if self.label_mode and self.label_mode == 'internal':  # solid theme
            pieces.append(self._render_with_internal_label())
        else:
            pieces.append(self._render())  # external

        if os_name == 'nt':  # Windows taskbar progress
            notify_progress(floor(self.ratio * 100))

        self._cached_str = rendered = ''.join(pieces)
        if self.debug:
            pieces.append(
                f'⇱ r:{self.ratio:5.3f} ncc:{self._num_complete_chars:2d} '
                f'rm:{self._remainder!r} '
                f'nec:{self._num_empty_chars:2d} '
                f'l:{len_stripped(rendered.lstrip(chr(13)))}'  # '\r' aka CR
            )
            self._cached_str = rendered = ''.join(pieces)  # again :-/

        return rendered

    def __repr__(self):
        return repr(self.__str__())

    def __call__(self, complete):
        ''' Sets the value of the bar graph. '''
        # convert ints to float from 0…1 per-one-tage
        self.ratio = ratio = complete / self.total
        if self.expand:
            if term_width != _term_width_orig:  # unix change
                self._set_bar_width()
            elif os_name == 'nt':  # need to explicitly check
                self._set_bar_width(get_size()[0])
        self._update_status(ratio)

        # find num complete and empty chars
        ncc = self._get_ncc(self._bwidth, ratio)  # for overriding
        if ncc < 0:  # restrict from 0 to _bwidth
            ncc = self._remainder = 0
        if ncc > self._bwidth:
            ncc = self._bwidth
            self._remainder = 0
        self._num_complete_chars = ncc
        self._num_empty_chars = self._bwidth - ncc

        self._cached_str = None  # clear cache
        return self

    def _get_ncc(self, width, ratio):
        ''' Get the number of completed whole characters. '''
        return round(self._bwidth * ratio)

    @property
    def clear_left(self):
        return self._clear_left

    @clear_left.setter
    def clear_left(self, value):
        ''' Converts a given integer to an escape sequence. '''
        if value is True:
            self._clear_left = '\r'  # do not use move_x, if term=dumb
        elif type(value) is int:
            move_x = sc.move_x
            if move_x is _empty:  # TERM=dumb
                self._clear_left = f'\r{" " * value}'
            else:  # = f'{clear_line(1)}{sc.move_x(value)}'  # not needed
                self._clear_left = f'\r{sc.move_x(value)}'
        elif value in (False, None):
            self._clear_left = value
        else:
            raise TypeError('clear_left: type %s is not valid.' % type(value))

    def reset(self):
        ''' Reset the bar, start time only for now. '''
        # dynamic label fmt, set to None to disable
        self._start = time.time()

    def _update_status(self, ratio):
        ''' Check bounds for errors and update label accordingly. '''
        # figure label
        label = label_unstyled = ''
        label_mode = self.label_mode
        label_fmt = self.label_fmt[0]

        # change label fmt based on time - when slow, go to higher-res display
        if self.timedeltas:
            delta = time.time() - self._start
            if delta > self.timedeltas[1]:
                label_fmt = self.label_fmt[2]
            elif delta > self.timedeltas[0]:
                label_fmt = self.label_fmt[1]

        if 0 <= ratio < 1:  # in progress
            if label_mode:
                label = label_unstyled = label_fmt % (ratio * 100)
            if self.oob_error:  # now fixed, reset
                self._first = self.styles[_if](self.icons[_if])
                self._last = self.styles[_il](self.icons[_il])
                self._comp_style = self.styles[_ic]
                self.oob_error = False
                self.done = False
        else:
            if ratio == 1:  # done
                self.done = True
                self._comp_style = self.styles[_id]
                self._last = self.styles[_if](self.icons[_il])
                if label_mode:
                    label = label_unstyled = self.label_fmt_str % self.icons[_id]
                if self.oob_error:  # now fixed, reset
                    self._first = self.styles[_if](self.icons[_if])
                    self.oob_error = False

            # error - out of bounds :-/
            elif ratio > 1:
                self.done = True
                self.oob_error = True
                self._last = self._err_style(self.icons[_ieh])
                if label_mode and not label_mode == 'internal':
                    label_unstyled = self.label_fmt_str % self.icons[_ieb]
                    label = self._err_style(label_unstyled)
            else:  # < 0
                self.oob_error = True
                self.done = False
                self._first = self._err_style(self.icons[_iel])
                if label_mode and not label_mode == 'internal':
                    label_unstyled = self.label_fmt_str % self.icons[_ieb]
                    label = self._err_style(label_unstyled)

        self._lbl = label
        # dynamic resizing of the bar, depending on label length:
        if label and label_mode != 'internal':
            self._bwidth = self._bwidth_base - len(label_unstyled) # or label)
        else:
            self._bwidth = self._bwidth_base

    def _render(self):
        ''' Standard rendering of bar graph. '''
        cm_chars = (    # completed
            self._comp_style(self.icons[_ic] * self._num_complete_chars)
        )
        em_chars = (    # empty
            self._empt_style(self.icons[_ie] * self._num_empty_chars)
        )
        return f'{self._first}{cm_chars}{em_chars}{self._last}{self._lbl}'

    def _render_with_internal_label(self):
        ''' Render with a label inside the bar graph. '''
        ncc = self._num_complete_chars
        bar = self._lbl.center(self._bwidth)
        cm_chars = self._comp_style(bar[:ncc])
        em_chars = self._empt_style(bar[ncc:])
        return f'{self._first}{cm_chars}{em_chars}{self._last}'


class HiDefProgressBar(ProgressBar):
    ''' A ProgressBar with increased, sub-character cell resolution,
        approx 8x.

        Most useful in constrained environments (a small terminal window)
        and/or long-running tasks.

        Arguments:
            width: 8 or greater
            partial_chars - sequence of characters to show progress
    '''
    icons = icons['segmented']
    min_width = 8
    partial_chars = ('░', '▏', '▎', '▍', '▌', '▋', '▊', '▉')
    partial_chars_len = len(partial_chars)
    # matching bg helps partial char look a bit more natural:
    partial_char_extra_style = bg.i236

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # partial chars may be in theme or passed as kwargs
        if 'theme' in kwargs:
            partial_chars = themes[kwargs['theme']].get('partial_chars')
            if partial_chars:
                self.partial_chars = partial_chars
                self.partial_chars_len = len(partial_chars)  # re-calc
            pc_es = themes[kwargs['theme']].get('partial_char_extra_style')
            if pc_es:
                self.partial_char_extra_style = pc_es

        if 'partial_chars' in kwargs:
            self.partial_chars_len = len(self.partial_chars)  # re-calc

    def _get_ncc(self, width, ratio):
        ''' Get the number of complete chars.

            This one figures the _remainder for the partial char as well.
        '''
        sub_chars = round(width * ratio * self.partial_chars_len)
        ncc, self._remainder = divmod(sub_chars, self.partial_chars_len)
        return ncc

    def _render(self):
        ''' figure partial character '''
        p_char = ''
        if not self.done and self._remainder:
            p_style = self._comp_style
            if self.partial_char_extra_style:
                if p_style is str:
                    p_style = self.partial_char_extra_style
                else:
                    p_style = p_style + self.partial_char_extra_style

            p_char = p_style(self.partial_chars[self._remainder])
            self._num_empty_chars -= 1

        cm_chars = self._comp_style(self.icons[_ic] * self._num_complete_chars)
        em_chars = self._empt_style(self.icons[_ie] * self._num_empty_chars)
        return f'{self._first}{cm_chars}{p_char}{em_chars}{self._last}{self._lbl}'


def install_resize_handler():
    ''' Signal handling code - handles the situation when full-width bars are
        created via expand = True, and the virtual terminal width changes.

        Note: Unix only
    '''
    if os_name != 'nt':
        import signal

        def _window_resize_handler(sig, frame):
            global term_width
            term_width = get_size()[0]

        signal.signal(signal.SIGWINCH, _window_resize_handler)


def progress(value: float,
        clear_left=ProgressBar._clear_left,
        expand=ProgressBar.expand,
        label_mode=ProgressBar.label_mode,
        list_themes=False,
        theme=ProgressBar.theme,
        total: int=DEF_TOTAL,
        width=ProgressBar.width,
        debug=bool(ProgressBar.debug),
    ):
    ''' Convenience function for building a one-off progress bar,
        for scripts and CLI, etc.

        Arguments:
            value                   The current value.
            clear_left: True        True to clear and mv to 0, or int offset
            debug: None             Enable debug output
            expand: False           Set width to full terminal width
            label_mode:  True       Enable progress percentage label
            total:  99              Set the total number of items
            width: 32               Full width of bar, padding, and labels

        Note:
            The value parameter is 0-based, therefore think 0-99,
            rather than 1-100.
            If you'd like value to signify a percentage instead,
            pass ``--total 100`` or other round number as well.

        Run ``python3 -m console.progress -l`` for a demo.
    '''
    debug = debug or log.isEnabledFor(logging.DEBUG)  # -v
    try:  # Yabba Dabba, DOO!
        if list_themes:
            return 'themes: ' + ' '.join(themes.keys())
        else:
            del list_themes

        if theme in ('hd_green', 'dies'):
            bar = HiDefProgressBar(**locals())
        else:
            bar = ProgressBar(**locals())
        result = bar(value)
        return result
    except Exception as err:
        log.exception(f'{err.__class__.__name__}: {err}')


if __name__ == '__main__':

    import sys
    from time import sleep

    # set defaults
    ProgressBar.debug = '-d' in sys.argv
    ProgressBar.label_mode = '-l' in sys.argv
    ProgressBar._clear_left = False  # new class default

    bars = [
        ('basic, expanded:\n',
                            ProgressBar(theme='basic', expand=True)),
        ('basic clr:',      ProgressBar(theme='basic_color')),
        ('* default:',      ProgressBar()),
        ('shaded:',         ProgressBar(theme='shaded')),
        ('bullets:',        ProgressBar(icons='bullets', styles='ocean8')),
        ('warm_shaded:',    ProgressBar(theme='warm_shaded')),
        ('faces:',          ProgressBar(theme='shaded', icons='faces')),
        ('wide_faces:',     ProgressBar(styles='simple', icons='wide_faces')),
        ('hvy_metal:',      ProgressBar(theme='heavy_metal')),
        ('segmented:',      ProgressBar(icons='segmented')),
        ('triangles:',      ProgressBar(theme='shaded', icons='triangles')),
        ('solid, expanded:\n',
                            ProgressBar(theme='solid', expand=True)),
        ('solid mono:',     ProgressBar(theme='solid', styles='amber_mono')),

        ('hd_green:',       HiDefProgressBar(styles='greyen')),
        ('dies:',           HiDefProgressBar(theme='dies', # clear_left=4,
                                             partial_char_extra_style=fg.lightred)),
    ]

    # print each in progress
    from console.utils import cls
    cls()

    with sc.hidden_cursor():
        try:
            for i in range(100):
                print()
                for label, bar in bars:
                    print(f' {label:12}', bar(i), sep='')

                sleep(.1)
                if i < 99:
                    cls()
            sleep(2)
        except KeyboardInterrupt:
            pass

    # print each with a number of values
    print()
    for label, bar in bars:

        # reset once
        if bar.done:
            bar.done = False
            bar._comp_style = bar.styles[_ic]
            bar._last = bar.styles[_il](bar.icons[_il])

        print(label)
        for complete in (-2, 0, 51, 99, 123):
            if bar.expand:
                print(bar(complete))
            else:
                print(' ', bar(complete))
        print()
