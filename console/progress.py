'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    Experimental - Progress Bar functionality.

    TODO:
        - themes: string indexes instead of ints
        - gradients/rainbar
        - Tests
'''
import time

from console import fg, bg, fx, _CHOSEN_PALETTE
from console.utils import len_stripped
from console.detection import (detect_unicode_support, get_available_palettes,
                               get_size)

TIMEDELTA_1 = 60
TIMEDELTA_2 = 300

# Theme-ing info
_if, _ic, _ie, _il, _id, _ir = range(6)  # indexes

icons = dict(
    # name      first, complete, empty, last, error
    ascii       = ('[', '#', '-', ']'),
    blocks      = (' ', '▮', '▯', ' '),
    bullets     = (' ', '•', '•', ' '),  # empty white bullet wrong size/align
    dies        = (' ', '⚅', '⚀', ' '),
    horns       = ('🤘', '⛧', '⛤', '🤘'),
    segmented   = ('▕', '▉', '▉', '▏'),
    faces       = (' ', '☻', '☹', ' '),
    wide_faces  = (' ', '😎', '😞', ' '),
    stars       = ('(', '★', '☆', ')'),
    shaded      = ('▕', '▓', '░', '▏'),
    triangles   = ('▕', '▶', '◁', '▏'),
    spaces      = ('▕', ' ', ' ', '▏'),
)

_dim_green = fx.dim + fg.green
_err_color = fg.lightred
styles = dict(
    dumb        = (str,) * 6,
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
    simple      = (
                    str,                # first
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

# TODO: not sure if this is useful
unicode_support = detect_unicode_support()
if unicode_support:
    icons['default']  = icons['blocks']
else:
    icons['default']  = icons['ascii']

# TODO: choose 256 color
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
    normal = dict(icons='ascii', styles='default'),
    shaded = dict(icons='shaded', styles='ocean'),
    solid = dict(icons='spaces', styles='greyen_bg'),
    warm_shaded = dict(icons='shaded', styles='amber'),
)
themes['default'] = themes['normal']


class ProgressBar:
    ''' A stylable bar graph for displaying progress of completion.

        Arguments:
            width: 10 or greater
    '''
    complete = 0
    debug = None
    done = False
    oob_error = False  # out of bounds
    full_width = False
    label_fmt = '%2.0f%%'
    label_mode = True
    min_width = 12
    remainder = 0
    timedelta1 = TIMEDELTA_1
    timedelta2 = TIMEDELTA_2
    total = 100
    unicode_support = unicode_support
    width = 32
    _num_complete_chars = 0

    theme = 'default'
    icons = icons[theme]
    styles = styles[theme]

    def __init__(self, **kwargs):
        self.start = time.time()  # dynamic label fmt, set to None to disable

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
            else:
                setattr(self, key, val)

        padding = len(self.icons[_if]) + len(self.icons[-1])
        if self.width < self.min_width:
            self.width = self.min_width
        if self.full_width:
            self.width = get_size()[0]
        self.iwidth = self.width - padding  # internal width

        # configure styles
        _styles = self.styles
        self._first = _styles[_if](self.icons[_if])
        self._comp_style = _styles[_ic]
        self._empt_style = _styles[_ie]
        self._last = _styles[_il](self.icons[_il])
        self._err_style = _styles[_ir]

    def __str__(self):
        ''' Renders the current state as a string. '''
        if self._cached_str:
            return self._cached_str

        if self.label_mode == 'internal':  # solid theme
            rendered = self._render_internal_label()
        else:
            rendered = self._render()

        if self.debug:
            rendered = (f'r:{self.ratio:5.2f} ncc:{self._num_complete_chars:2d} '
                        #~ f'cr:{self.iwidth * self.ratio / self.total:5.2f} '
                        f'rm:{self.remainder!r} '
                        f'nec:{self._num_empty_chars:2d} '
                        f'{rendered} l:{len_stripped(rendered)}')

        self._cached_str = rendered = rendered.rstrip()
        return rendered

    def __call__(self, complete):
        ''' Sets the value of the bar graph. '''
        # convert ints to float from 0…1 per-one-tage
        self.ratio = ratio = complete / self.total

        # find num complete and empty chars
        ncc = self._get_ncc(self.iwidth, ratio)  # for overriding
        if ncc < 0:  # restrict from 0 to iwidth
            ncc = self.remainder = 0
        if ncc > self.iwidth:
            ncc = self.iwidth
            self.remainder = 0
        self._num_complete_chars = ncc
        self._num_empty_chars = self.iwidth - ncc

        self._update_status()
        self._cached_str = None
        return self

    def _get_ncc(self, width, ratio):
        ''' Get the number of completed whole characters. '''
        return round(self.iwidth * ratio)

    def _update_status(self):
        ''' Check bounds for errors and update label accordingly. '''
        label = ''
        # label format, based on time - when slow, go to higher-res display
        delta = time.time() - self.start
        if delta > self.timedelta2:
            self.label_fmt = '%5.2f%%'
        elif delta > self.timedelta1:
            self.label_fmt = '%4.1f%%'

        ratio = self.ratio
        if 0 <= ratio < 1:
            if self.label_mode:
                label = self.label_fmt % (ratio * 100)
            if self.oob_error:  # now fixed, reset
                self._first = self.styles[_if](self.icons[_if])
                self._last = self.styles[_il](self.icons[_il])
                self.oob_error = False
                self._comp_style = self.styles[_ic]
                self.done = False
        else:
            if ratio == 1:
                self.done = True
                self._comp_style = self.styles[_id]
                self._last = self.styles[_if](self.icons[_il])
                if self.label_mode:
                    label = '✓' if self.unicode_support else '+'
                if self.oob_error:  # now fixed, reset
                    self._first = self.styles[_if](self.icons[_if])
                    self.oob_error = False

            elif ratio > 1:
                self.done = True
                self.oob_error = True
                if self.unicode_support:
                    self._last = self._err_style('⏵')
                    if self.label_mode:
                        label = '✗'
                else:
                    self._last = self._err_style('>')
                    if self.label_mode:
                        label = 'ERR'
            else:  # < 0
                self.oob_error = True
                if self.unicode_support:
                    self._first = self._err_style('⏴')
                    if self.label_mode:
                        label = '✗'
                else:
                    self._first = self._err_style('<')
                    if self.label_mode:
                        label = 'ERR'
        self._lbl = label

    def _render(self):
        ''' Standard rendering of bar graph. '''
        cm_chars = self._comp_style(self.icons[_ic] * self._num_complete_chars)
        em_chars = self._empt_style(self.icons[_ie] * self._num_empty_chars)
        return f'{self._first}{cm_chars}{em_chars}{self._last} {self._lbl}'

    def _render_internal_label(self):
        ''' Render with a label inside the bar graph. '''
        ncc = self._num_complete_chars
        bar = self._lbl.center(self.iwidth)
        cm_chars = self._comp_style(bar[:ncc])
        em_chars = self._empt_style(bar[ncc:])
        return f'{self._first}{cm_chars}{em_chars}{self._last}'


class HiDefProgressBar(ProgressBar):
    ''' A ProgressBar with increased, sub-character cell resolution,
        approx 8x.

        Most useful in constrained environments, i.e. a small terminal window.

        Arguments:
            width: 7 or greater
            partial_chars - sequence of characters to show progress
    '''
    icons = icons['segmented']
    min_width = 7
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

            This one figures the remainder for the partial char as well.
        '''
        sub_chars = round(width * ratio * self.partial_chars_len)
        ncc, self.remainder = divmod(sub_chars, self.partial_chars_len)
        return ncc

    def _render(self):
        ''' figure partial character '''
        p_char = ''
        if not self.done and self.remainder:
            p_style = self._comp_style
            if self.partial_char_extra_style:
                if p_style is str:
                    p_style = self.partial_char_extra_style
                else:
                    p_style = p_style + self.partial_char_extra_style

            p_char = p_style(self.partial_chars[self.remainder])
            self._num_empty_chars -= 1

        cm_chars = self._comp_style(self.icons[_ic] * self._num_complete_chars)
        em_chars = self._empt_style(self.icons[_ie] * self._num_empty_chars)
        return f'{self._first}{cm_chars}{p_char}{em_chars}{self._last} {self._lbl}'


if __name__ == '__main__':

    import sys

    # set defaults
    ProgressBar.debug = '-d' in sys.argv
    ProgressBar.label_mode = '-l' in sys.argv

    bars = [
        ('basic',       ProgressBar(theme='basic')),
        ('basic clr',   ProgressBar(theme='basic_color')),
        ('* default',   ProgressBar()),
        ('shaded',      ProgressBar(theme='shaded')),
        ('warm-shaded', ProgressBar(theme='warm_shaded')),
        ('faces',       ProgressBar(theme='shaded', icons='faces')),
        #~ # ('wide faces',  ProgressBar(style='simple', icons='wide_faces')),
        ('hvy-metal',   ProgressBar(theme='heavy_metal')),
        ('segmented',   ProgressBar(icons='segmented')),
        ('triangles',   ProgressBar(theme='shaded', icons='triangles')),
        ('solid',       ProgressBar(theme='solid')),
        ('solid mono',  ProgressBar(theme='solid', styles='amber_mono')),
        ('partial',     HiDefProgressBar(styles='greyen')),

        ('dies',        HiDefProgressBar(theme='dies',
                                         partial_chars='⚀⚁⚂⚃⚄⚅',
                                         partial_char_extra_style=None)),
    ]

    from console.utils import cls
    from console.screen import sc

    # print each in progress
    cls()
    with sc.hidden_cursor():
        try:
            for i in range(0, 101):
                print()
                for label, bar in bars:
                    print(f'  {label + ":":12}', bar(i))

                time.sleep(.2)
                if i != 100:
                    cls()
            time.sleep(1)
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
            bar.label_fmt = ProgressBar.label_fmt

        print(label + ':')
        #~ # for complete in (-2, 0, 51, 100, 150, 84, 100):
        for complete in (-2, 0, 51, 100, 150):
            print(' ', bar(complete))
        print()
