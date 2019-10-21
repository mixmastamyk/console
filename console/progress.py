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
import time

from . import fg, bg, fx, _CHOSEN_PALETTE
from .disabled import empty as _empty
from .screen import sc
from .utils import len_stripped
from .detection import (detect_unicode_support, get_available_palettes,
                               get_size, os_name)

TIMEDELTAS = (60, 300)  # accuracy thresholds, in seconds, one and five minutes
MIN_WIDTH = 12
_END = str(fx.end)      # fbterm support

# Theme-ing info:
icons = dict(
    # name:      first, complete, empty, last, done, err_lo, err_hi, err_lbl
    ascii       = ('[', '#', '-', ']', '+', '<', '>', 'ERR'),
    blocks      = (' ', '▮', '▯', ' ', '✓', '⏴', '⏵', '✗'),
    # empty white bullet is the wrong size, breaks alignment:
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
_err_color = fg.lightred
styles = dict(
    dumb        = (_empty,) * 6,
    amber       = (
                    fx.dim + fg.i208,   # first
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
    simple      = ( # str no longer works, call broke fbterm, so using ''
                    str,                # first,
                    str,                # complete
                    fx.dim,             # empty
                    str,                # last
                    fx.dim,             # done
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
    ocean       = (
                    _dim_green,         # first
                    fg.green,           # complete
                    fg.blue,            # empty
                    fx.dim + fg.blue,   # last
                    _dim_green,         # done
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
                    fx.dim + fg.i70,    # first
                    fx.bold + bg.i70,   # complete
                    fx.dim + bg.i236,   # empty
                    fx.dim + fg.i236,   # last
                    bg.i22,             # done
                    _err_color,         # error
                  ),
)

# figure default styles
unicode_support = detect_unicode_support()
icons['default']  = icons['ascii']
if os_name == 'nt':  # default to ascii on Windows
    pass
elif unicode_support:
    icons['default']  = icons['blocks']

_pals = get_available_palettes(_CHOSEN_PALETTE)
if _pals and 'extended' in _pals:
    styles['default'] = styles['ocean8']
elif _pals:
    styles['default'] = styles['ocean']
else:
    styles['default'] = styles['dumb']

themes = dict(
    basic_color = dict(icons='ascii', styles='default'),
    basic = dict(icons='ascii', styles='dumb'),
    dies = dict(icons='dies', styles='simple'),
    heavy_metal = dict(icons='horns', styles='reds'),
    shaded = dict(icons='shaded', styles='ocean'),
    solid = dict(icons='spaces', styles='greyen_bg'),
    warm_shaded = dict(icons='shaded', styles='amber'),
)
themes['default'] = themes['basic_color']


class ProgressBar:
    ''' A stylable bar graph for displaying the current progress of task
        completion.

        Example::

            import time  # demo purposes only
            from console.screen import sc
            from console.progress import ProgressBar

            with sc.hidden_cursor():

                items = range(256)      # example tasks
                bar = ProgressBar(total=len(items))  # set total

                for i in items:
                    print('Caption:', bar(i), end='', flush=True)
                    time.sleep(.1)
                print()

                # or use as a tqdm-style iterable wrapper:
                for i in ProgressBar(range(100)):
                    sleep(.1)

        Arguments:
            clear_left: True        True to clear and mv to 0, or int offset
            debug: None             Turn on debug output
            done: False             True on completion, moderates style
            expand: False           Set width to full terminal width
            iterable: object        An object to iterate on.
            label_mode:  True       Turn on label
            oob_error:  False       Out of bounds error occurred
            total:  100             Set the total number of items
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
    unicode_support = unicode_support
    width = 32

    theme = 'default'
    icons = icons[theme]
    styles = styles[theme]

    _clear_left = True
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
                self.width = get_size()[0]
                self.expand = val
            else:
                setattr(self, key, val)

        # figure widths
        _icons = self.icons
        if self.width < self._min_width:
            self.width = self._min_width
        # padding: first, last bookends
        self.padding = len(_icons[_if]) + len(_icons[_il])
        # save bar width
        self._bwidth = self._bwidth_orig = (self.width - self.padding)
        if self._clear_left is True:
            self.clear_left = self._clear_left  # render

        # configure styles
        _styles = self.styles
        self._comp_style = _styles[_ic]
        self._empt_style = _styles[_ie]
        self._err_style = _styles[_iel]
        self._first = _styles[_if](_icons[_if])
        self._last = _styles[_il](_icons[_il])

        # dynamic label fmt, set to None to disable
        self._start = time.time()

        # tqdm-style iterable interface
        if iterable and not self.total:
            try:
                self.total = len(iterable)
            except (TypeError, AttributeError):
                self.total = None
            self.iterable = iterable
            self(self._iter_n)  # call() set initial
        else:
            self.total = 100

    def __len__(self):
        return self.total

    def __iter__(self):
        ''' tqdm-style iterable interface: https://tqdm.github.io/ '''
        for obj in self.iterable:
            yield obj
            self._iter_n += 1
            self(self._iter_n)
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
            pieces.append(self._render())

        self._cached_str = rendered = ''.join(pieces)
        if self.debug:
            pieces.append(
                f'⇱ r:{self.ratio:5.2f} ncc:{self._num_complete_chars:2d} '
                f'rm:{self._remainder!r} '
                f'nec:{self._num_empty_chars:2d} '
                f'l:{len_stripped(rendered)}'
            )
            self._cached_str = rendered = ''.join(pieces)  # again :-/
        return rendered

    def __repr__(self):
        return repr(self.__str__())

    def __call__(self, complete):
        ''' Sets the value of the bar graph. '''
        # convert ints to float from 0…1 per-one-tage
        self.ratio = ratio = complete / self.total
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
            value = 0
        if type(value) is int:
            #~ self._clear_left = f'{clear_line(1)}{sc.mv_x(value)}'
            self._clear_left = f'\r{sc.mv_x(value)}'
        elif type(value) in (bool, type(None)):
            self._clear_left = value
        else:
            raise TypeError('type %s not valid.' % type(value))

    def _update_status(self, ratio):
        ''' Check bounds for errors and update label accordingly.

            fbterm support: can't use call() if combined with other styles
                            since they get rendered as strings due to differing
                            escape sequences.  See _END for locations.
        '''
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
                label = label_fmt % (ratio * 100)
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
                    label = self.label_fmt_str % self.icons[_id]
                if self.oob_error:  # now fixed, reset
                    self._first = self.styles[_if] + self.icons[_if] + _END
                    self.oob_error = False

            # error - out of bounds :-/
            elif ratio > 1:
                self.done = True
                self.oob_error = True
                # fbterm - can't use call() if combined:
                self._last = self._err_style + self.icons[_ieh] + _END
                if label_mode and not label_mode == 'internal':
                    label_unstyled = self.label_fmt_str % self.icons[_ieb]
                    label = self._err_style + label_unstyled + _END
            else:  # < 0
                self.oob_error = True
                self._first = self._err_style(self.icons[_iel])
                if label_mode and not label_mode == 'internal':
                    label_unstyled = self.label_fmt_str % self.icons[_ieb]
                    label = self._err_style + label_unstyled + _END

        self._lbl = label
        # dynamic resizing of the bar, depending on label length:
        if label and label_mode != 'internal':
            self._bwidth = self._bwidth_orig - len(label_unstyled or label)

    def _render(self):
        ''' Standard rendering of bar graph. '''
        cm_chars = (
            self._comp_style + (self.icons[_ic] * self._num_complete_chars) + _END
        )
        em_chars = (
            self._empt_style + (self.icons[_ie] * self._num_empty_chars) + _END
        )
        return f'{self._first}{cm_chars}{em_chars}{self._last}{self._lbl}'

    def _render_with_internal_label(self):
        ''' Render with a label inside the bar graph. '''
        ncc = self._num_complete_chars
        bar = self._lbl.center(self._bwidth)
        cm_chars = self._comp_style + bar[:ncc] + _END
        em_chars = self._empt_style + bar[ncc:] + _END
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
        if 'partial_chars' in kwargs:  # re-calc
            self.partial_chars_len = len(self.partial_chars)

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


if __name__ == '__main__':

    import sys

    # set defaults
    ProgressBar.debug = '-d' in sys.argv
    ProgressBar.label_mode = '-l' in sys.argv
    ProgressBar._clear_left = False  # class default

    bars = [
        ('basic, expanded:\n',
                            ProgressBar(theme='basic', expand=True)),
        ('basic clr:',      ProgressBar(theme='basic_color')),
        ('* default:',      ProgressBar()),
        ('shaded:',         ProgressBar(theme='shaded')),
        ('bullets:',        ProgressBar(icons='bullets', style='ocean8')),
        ('warm-shaded:',    ProgressBar(theme='warm_shaded')),
        ('faces:',          ProgressBar(theme='shaded', icons='faces')),
        # ('wide faces:',     ProgressBar(style='simple', icons='wide_faces')),
        ('hvy-metal:',      ProgressBar(theme='heavy_metal')),
        ('segmented:',      ProgressBar(icons='segmented')),
        ('triangles:',      ProgressBar(theme='shaded', icons='triangles')),
        ('solid, expanded:\n',
                            ProgressBar(theme='solid', expand=True)),
        ('solid mono:',     ProgressBar(theme='solid', styles='amber_mono')),

        ('high-def:',       HiDefProgressBar(styles='greyen')),
        ('dies:',           HiDefProgressBar(theme='dies', # clear_left=4,
                                             partial_chars='⚀⚁⚂⚃⚄⚅',
                                             partial_char_extra_style=None)),
    ]

    # print each in progress
    from console.utils import cls
    cls()

    with sc.hidden_cursor():
        try:
            for i in range(0, 101):
                print()
                for label, bar in bars:
                    print(f' {label:12}', bar(i), sep='')

                time.sleep(.1)
                if i != 100:
                    cls()
            time.sleep(2)
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
        #~ # for complete in (-2, 0, 51, 100, 150, 84, 100):
        for complete in (-2, 0, 51, 100, 155):
            if bar.expand:
                print(bar(complete))
            else:
                print(' ', bar(complete))
        print()
