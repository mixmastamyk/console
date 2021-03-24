# -*- coding: future_fstrings -*-
'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2020, Mike Miller - Released under the LGPL, version 3+.

    An EXPERIMENTAL module containing an HTML to ANSI sequence converter.
    It supports quick rich-text in scripting applications for those familiar
    with HTML.  Why invent another styling language?

    Currently is partially useful.  No CSS class support yet,
    but many inline styles that correspond to terminal capabilities work.
'''
import re
import logging
from os.path import splitext
from enum import Enum, auto

from . import fg, bg, fx, defx
from .utils import make_hyperlink, make_line, make_sized
from .detection import _sized_char_support, get_size

from html.parser import HTMLParser


HALF2FULL = dict((i, i + 0xFEE0) for i in range(0x21, 0x7F))  # Wide ASCII map
HALF2FULL[0x20] = 0x3000  # https://stackoverflow.com/a/36693548/450917
log = logging.getLogger(__name__)
debug = log.debug
fx_tags = ('b', 'i', 's', 'u', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong')
skip_data_tags = ('script', 'style', 'title')
block_tags = '''address article aside canvas dd div dl dt fieldset figcaption
figure footer form header main nav noscript p sectiontable tfoot video
'''.split()
# blockquote h1-h6 hr pre ul ol li https://www.w3schools.com/htmL/html_blocks.asp
multi_whitespace_hunter = re.compile(r'\s\s+')
_width = get_size().columns


# find html header mode for rendering
class HeaderMode(Enum):
    NORMAL = auto()
    FIGLET = auto()
    DOUBLE = auto()


if _sized_char_support:
    header_mode = HeaderMode.DOUBLE
    _double_fonts = dict(
        h1=dict(double=True),  # + bold
        h2=dict(double=True),
        h3=dict(double=False, wide=True),  # + bold
        h4=dict(double=False, wide=True),
    )

else:
    try:
        import sys
        if '-i' in sys.argv:  # testing
            raise ImportError
        from pyfiglet import Figlet  # gettin' figgy with it, na na na…
        header_mode = HeaderMode.FIGLET
        Figlet.render = Figlet.renderText
        _figlet_fonts = dict(
            h1=Figlet(font='standard', width=_width),
            h2=Figlet(font='small', width=_width),
            #~ h3=Figlet(font='wideterm', width=_width),
        )
    except ImportError:
        header_mode = HeaderMode.NORMAL


class StringCache(dict):
    ''' Used to cache rendered ANSI color/fx strings with a dictionary lookup
        interface.
    '''
    def __init__(self, palette, **kwargs):
        self._palette = palette
        # allows renames to happen, currently supports em --> i
        self._renames = kwargs

    def __missing__(self, key):
        ''' Not found, render, save, return. '''
        if _sized_char_support and key[0] == 'h':
            if key[1] in '24':  # disable styles on even headers
                return ''

        key = self._renames.get(key, key)
        if key.startswith('#'):                 # handle hex colors
            key = 't' + key[1:]

        entry = None  # there might be more than one, delimited by commas.
        for sub_key in key.split(','):
            next_entry = getattr(self._palette, sub_key)
            if entry:
                entry += next_entry  # add together
            else:
                entry = next_entry

        val = str(entry)  # render palette entry
        self[key] = val
        #~ debug('missing called with: %r, returned %r', key, val)
        return val


class LiteHTMLParser(HTMLParser):
    ''' Parses simple HTML tags, returns as text and ANSI sequences.

        Exmaple::

            parser = LiteHTMLParser()
            parser.feed(text)
            result = ''.join(parser.tokens)  # build and return final string
            parser.tokens.clear()

    '''
    _anchor = []
    tokens = []
    _setting_bg_color = None
    _setting_fg_color = _setting_fg_color_dim = None
    _setting_font_style = _setting_font_weight = None
    _setting_text_decoration_u = _setting_text_decoration_o = None
    _skip_data = None
    _preformatted_data = None
    _list_mode = None
    _blockquote = None
    _in_header = None

    def _to_full_width(self, data, is_ascii):
        ''' Converts ASCII characters to their full-width counterpart,
            adds spaces for the rest.
            https://stackoverflow.com/a/36693548/450917
        '''
        if is_ascii:
            data = data.translate(HALF2FULL)  # widen with wide chars
        else:
            data = ' '.join(data)  # widen with spaces
        return data

    def _set_fg_color(self, val):
        self.tokens.append(fg_cache[val])
        self._setting_fg_color = True

    def _set_bg_color(self, val):
        self.tokens.append(bg_cache[val])
        self._setting_bg_color = True

    def _set_fg_color_default(self):
        self.tokens.append(fg_cache['default'])
        self._setting_fg_color = False

    def _set_bg_color_default(self):
        self.tokens.append(bg_cache['default'])
        self._setting_bg_color = False

    def _new_paragraph(self, desc='start'):  # max two newlines at a time
        tokens = self.tokens
        try:
            if tokens:
                last = tokens[-1]
                if last.endswith('\n'):
                    if last.endswith('\n\n'):   # cap newlines at two
                        pass
                    elif last == '\n':
                        if tokens[-2].endswith('\n'):  # penultimate
                            pass
                        else:
                            tokens.append('\n')
                    else:
                        tokens.append('\n')
                else:
                    tokens.append('\n\n')   # in full effect
            else:
                tokens.append('\n')
        except IndexError:
            tokens.append('\n')

    def _handle_start_span(self, attrs):
        ''' Put bulky span/style/css handling here. '''
        for key, val in attrs:
            if key == 'style':
                for pair in val.split(';'):
                    prop, _, prop_val = [
                        x.strip() for x in pair.partition(':')
                    ]
                    if prop == 'color':
                        self._set_fg_color(prop_val)
                    elif prop in ('background', 'background-color'):
                        self._set_bg_color(prop_val)
                    elif prop == 'font-style' and prop_val == 'italic':
                        self.tokens.append(fx_cache['i'])
                        self._setting_font_style = True
                    elif prop == 'font-weight' and prop_val == 'bold':
                        self.tokens.append(fx_cache['b'])
                        self._setting_font_weight = True
                    elif prop == 'text-decoration':
                        if prop_val == 'underline':
                            self.tokens.append(fx_cache['u'])
                            self._setting_text_decoration_u = True
                        elif prop_val == 'overline':
                            self.tokens.append(fx_cache['overline'])
                            self._setting_text_decoration_o = True

    def _handle_header_styles(self, tag, data):
        ''' Header shizzle moved in here. '''
        # inspect data to find best rendition
        try:
            is_ascii = data.isascii()   # 3.7
        except AttributeError:          # :-/
            try:
                data.encode('ascii')
                is_ascii = True
            except UnicodeEncodeError:
                is_ascii = False

        if is_ascii:
            is_latin1 = False
        else:
            try:
                data.encode('latin1', errors='strict')
                is_latin1 = True
            except UnicodeEncodeError:
                is_latin1 = False

        # -- Double DECember -------------------------------------------------
        if header_mode is HeaderMode.DOUBLE and (is_ascii or is_latin1):
            font = _double_fonts.get(tag)
            if font:
                data = make_sized(data, **font)
            else:
                data = self._to_full_width(data, is_ascii)
            styled_data = f'{fx_cache[tag]}{data}{dx_cache[tag]}'
            self.tokens.append(styled_data)

        # -- Figlet ----------------------------------------------------------
        elif (
                header_mode is HeaderMode.FIGLET and
                tag in _figlet_fonts.keys() and
                is_ascii
            ):
            font = _figlet_fonts.get(tag)
            if font:
                self.tokens.append(font.render(data))

        # -- Text + ANSI -----------------------------------------------------
        else:  # normal
            if tag in ('h1', 'h2'):
                data = data.upper()

            data = self._to_full_width(data, is_ascii)
            if tag == 'h1':  # Style first, then center, harder than it sounds:
                len_data = len(data) * 2  # wide ascii, but not asian widths
                padding = (_width - len_data) // 2
                styled_data = f'{fx_cache[tag]}{data}{dx_cache[tag]}'
                centered_data = f'{padding * " "}{styled_data}'
                self.tokens.append(centered_data)
            else:
                styled_data = f'{fx_cache[tag]}{data}{dx_cache[tag]}'
                self.tokens.append(styled_data)

    def handle_data(self, data):
        ''' Deals with text between and outside the tags.  Cases::

                ' '
                ' word\n    '
                '\n    '
                '\n    word'
                'word', 'word ', ' word'

        '''
        debug('data0: %r', data)
        if self._skip_data:
            pass
        elif self._anchor:
            self._anchor.append(data)  # caption
        elif self._in_header:  # tag, add styling
            self._handle_header_styles(self._in_header, data)
        elif self._preformatted_data:
            self.tokens.append(data.lstrip('\n'))  # new para already
        else:
            tokens = self.tokens
            new_line = tokens and tokens[-1].endswith('\n')
            if data.startswith('\n'):  # at the end of each line
                data = data.lstrip()
                if tokens and not new_line:
                    data = ' ' + data  # give breathing room
                elif not data:
                    return
                debug('data1: %r', data)

            if new_line:
                data = data.lstrip()
                debug('data2: %r', data)

            # consolidate remaining whitespace to a single space:
            data = multi_whitespace_hunter.sub(' ', data)
            if self._blockquote:  # seems to come in lines
                data = (f'    {fx_cache["dim"]}│{dx_cache["dim"]} '
                        f'{fx_cache["i"]}{data}{dx_cache["i"]}')

            tokens.append(data)
        debug('tokens: %r\n', self.tokens)

    def handle_starttag(self, tag, attrs):
        debug('start tag: %s', tag)
        if tag in fx_tags:
            if tag.startswith('h'):
                self._new_paragraph()
                self._in_header = tag
            else:
                self.tokens.append(fx_cache[tag])
        else:
            if tag == 'span':
                self._handle_start_span(attrs)

            elif tag == 'a':
                for key, val in attrs:
                    if key == 'href':
                        self._anchor.append(val)  # target

            elif tag == 'br':
                self.tokens.append('\n')

            elif tag == 'c':
                fore = True
                for key, val in attrs:
                    if key == 'on':
                        fore = False; continue
                    if key == 'dim' and fore:  # consider dim a color
                        self.tokens.append(fx_cache[key])
                        self._setting_fg_color_dim = True
                    elif fore:
                        self._set_fg_color(key)  # <-- key, not val!
                        fore = False  # 'on' not needed
                    else:
                        self._set_bg_color(key)  # <-- key, not val!

            elif tag == 'font':
                for key, val in attrs:
                    if key == 'color':
                        self._set_fg_color(val)

            elif tag == 'q':
                self.tokens.append('“')

            elif tag == 'hr':
                self._new_paragraph()
                self.tokens.append(make_line())
                self._new_paragraph()

            elif tag == 'pre':
                self._new_paragraph()
                self._preformatted_data = True

            elif tag == 'blockquote':
                self._new_paragraph()
                self._blockquote = True

            elif tag == 'ul':
                self._new_paragraph()
                self._list_mode = 'ul'

            elif tag == 'ol':
                self._new_paragraph()
                self._list_mode = 1

            elif tag == 'li':
                mode = self._list_mode
                if mode == 'ul':
                    bullet = '•'
                else:
                    bullet = f'{mode}.'  # below could be nested  :-/
                    self._list_mode = (self._list_mode or 0) + 1
                self.tokens.append(f'  {bullet} ')

            elif tag in block_tags:  # behind pre, hr, etc
                self._new_paragraph()

            elif tag in skip_data_tags:
                self._skip_data = True

    def handle_endtag(self, tag):
        debug('end tag: %s', tag)
        if tag in fx_tags:
            if tag.startswith('h'):
                self._new_paragraph(desc='  end')
                self._in_header = False
            else:
                self.tokens.append(dx_cache[tag])
            if tag == 'h1' and _sized_char_support:  # xterm: one more nl,
                self.tokens.append('\n')  # underline is too close
        else:
            if tag == 'span':  # no elifs, could be multiple
                if self._setting_fg_color:
                    self._set_fg_color_default()
                if self._setting_bg_color:
                    self._set_bg_color_default()
                if self._setting_font_style:
                    self.tokens.append(dx_cache['i'])
                    self._setting_font_style = False
                if self._setting_font_weight:
                    self.tokens.append(dx_cache['b'])
                    self._setting_font_weight = False
                if self._setting_text_decoration_u:
                    self.tokens.append(dx_cache['u'])
                    self._setting_text_decoration_u = False
                if self._setting_text_decoration_o:
                    self.tokens.append(dx_cache['overline'])
                    self._setting_text_decoration_o = False

            elif tag == 'a':
                self._set_fg_color('lightblue')
                target, caption = self._anchor[0], ''.join(self._anchor[1:])
                self.tokens.append(make_hyperlink(target, caption, icon=''))  # 🔗?
                self._set_fg_color_default()
                self._anchor.clear()

            elif tag == 'c':
                if self._setting_fg_color:
                    self._set_fg_color_default()
                if self._setting_bg_color:  # no elif, could be multiple
                    self._set_bg_color_default()
                if self._setting_fg_color_dim:  # consider dim a color
                    self.tokens.append(dx_cache['dim'])
                    self._setting_fg_color_dim = False

            elif tag == 'font':
                if self._setting_fg_color:
                    self._set_fg_color_default()

            elif tag == 'q':
                self.tokens.append('”')

            elif tag == 'pre':
                self._preformatted_data = False
                self._new_paragraph()

            elif tag == 'blockquote':
                self._blockquote = False
                #~ self.tokens.append('”')
                self._new_paragraph()

            elif tag in ('ul', 'ol'):
                self._list_mode = None
                self._new_paragraph()

            elif tag == 'li':
                self.tokens.append('\n')

            elif tag in block_tags:
                self._new_paragraph()

            elif tag in skip_data_tags:
                self._skip_data = False

fg_cache = StringCache(fg)
bg_cache = StringCache(bg)
fx_cache = StringCache(
    fx, em='i', h1='b,u', h2='b', h3='b', h4='i', h5='b', h6='i', strong='b'
)
# disables individual styles, must match above
dx_cache = StringCache(
    defx, em='i', h1='b,u', h2='b', h3='b', h4='i', h5='b', h6='i', strong='b'
)
parser = LiteHTMLParser()


def hprint(*args, newline=False, **kwargs):
    ''' Print function for terminals, with limited HTML support. '''
    end = kwargs.pop('end', None)

    for arg in args:
        result = hrender(arg)

        debug('called with: %r %s', result, kwargs)
        print(result, end='', **kwargs)

    if not newline:
        print(end=end)


def hrender(text):
    ''' Renders HTML to an ANSI-compatible string. '''
    if '<' in text:
        parser.feed(text)
        result = ''.join(parser.tokens)
        parser.tokens.clear()
    else:
        result = text
    return result


def view(path):
    ''' Display text files, converting formatting to equivalent ANSI escapes.
        Currently supports limited-HTML only.
    '''
    result = ''
    if splitext(path)[1] in ('.html', '.htm'):
        with open(path) as infile:
            parser.feed(infile.read())
            result = ''.join(parser.tokens)
            parser.tokens.clear()
    return result


if __name__ == '__main__':

    import sys

    if '-d' in sys.argv:
        try:
            import out
            out.configure(level='debug')
        except ImportError:
            logging.basicConfig(level='DEBUG',
                format=('%(levelname)s '
                f'{fx.dim}%(funcName)s:{fg.green}%(lineno)s{fg.default}{defx.dim}'
                ' %(message)s'),
            )

    html = '''
    <script> var Mr_Bill = "Oh No!"; // nothing to see here </script>
    <style foo=bar>Dad { how-bout-you: "shut yer big YAPPER" !important; }</style>
    <h1>H1. HTML Print Test</h1>
    <h1>I ♥ ラーメン</h1>
    <c dim>fx:</c> <b>bold</b> <i>italic</i><em>/em</em> <s>strike</s>
    <u>undy</u><br>
    ¶<c dim>(span tag)</c>
    To<span style="color: red">Bill</span> Brasky!
    To <span style="color: red">Bill</span>Brasky!
    <b><span style=background:green>gr&euro;&euro;n</span></b>
      <c dim>(w/ entities)</c>
    <span style="color:cyan;font-style:italic;font-weight:bold">cyan</span>
    <span style="background: yellow; color: black">yellow</span>
    <span style="color:#444;text-decoration:overline;text-decoration: underline">
        #444</span> <c dim>(web/hex colors)</c><br>
    <c dim>(font tag)</c>
    <font color=blue>blue </font> <font color=purple> purple</font><br>
    <c dim>(c/color tag, with web/X11 color names)</c>
    <c orange>l'orange</c>
    <c black on bisque3>bisque3</c>
    <hr>
    <h2>H2. Part II</h2>
    <c #b0b>B0B</c> -&gt; <a href="http://example.com/">click here!</a>
    <p>
        A bit of <q>plain text</q> in its own paragraph.
    </p>
    <pre>
        var canvas = document.getElementById('myCanvas');
        var context = canvas.getContext('2d');
    </pre>
    <blockquote>
        This is a blockquote.
        This is a long line.<br>
        This is a long line.
        This is a long line.
        This is a long line.
    </blockquote>
    <!-- nothing in this comment should be shown, Buh-BYE ! -->
    Hello <h3>H3. woild!</h3><h4>H4. Heré</h4><h5>H5. Here</h5><h6>H6. Here</h6>
    ;-) '''
    hprint(html)
