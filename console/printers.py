'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2020, Mike Miller - Released under the LGPL, version 3+.

    This module contains an HTML to ANSI sequence printer,
    inspired by the "rich" project.
    It supports quick scripting applications for those familiar with HTML.

    No CSS class support yet,
    but many inline styles that correspond to terminal capabilities work.
'''
import re
import logging

from console import fg, bg, fx, defx
from console.utils import make_hyperlink

from html.parser import HTMLParser


log = logging.getLogger(__name__)
debug = log.debug
fx_tags = ('b', 'i', 's', 'u', 'em', 'h1', 'h2', 'h3', 'strong')
multi_whitespace_hunter = re.compile(r'\s\s+')


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
    ''' Parses simple HTML tags, returns as text and ANSI sequences. '''
    anchor = []
    tokens = []
    _setting_bg_color = None
    _setting_fg_color = _setting_fg_color_dim = None
    _setting_font_style = _setting_font_weight = None
    _setting_text_decoration_u = _setting_text_decoration_o = None

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
        if tokens:
            last = tokens[-1]
            if last.endswith('\n\n'):   # cap newlines at two
                pass
            elif last.endswith('\n'):   # ends with
                tokens.append('\n')
            else:
                tokens.append('\n\n')   # in full effect
        else:
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

    def handle_data(self, data):
        ''' Deals with text between and outside the tags.  Cases:
            ' '
            ' word\n    '
            '\n    '
            '\n    word'
            'word', 'word ', ' word'
        '''
        debug('data0: %r', data)
        if self.anchor:
            self.anchor.append(data)  # caption
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
            tokens.append(data)
        debug('tokens: %r\n', self.tokens)

    def handle_starttag(self, tag, attrs):
        debug('start tag: %s', tag)
        if tag in fx_tags:
            if tag.startswith('h'):
                self._new_paragraph()
            self.tokens.append(fx_cache[tag])
        else:
            if tag == 'span':
                self._handle_start_span(attrs)

            elif tag == 'a':
                for key, val in attrs:
                    if key == 'href':
                        self.anchor.append(val)  # target

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
                    else:
                        self._set_bg_color(key)  # <-- key, not val!

            elif tag == 'font':
                for key, val in attrs:
                    if key == 'color':
                        self._set_fg_color(val)

            elif tag == 'p':
                self._new_paragraph()

            elif tag == 'q':
                self.tokens.append('“')

    def handle_endtag(self, tag):
        debug('end tag: %s', tag)
        if tag in fx_tags:
            self.tokens.append(dx_cache[tag])
            if tag.startswith('h'):
                self._new_paragraph(desc='  end')
        else:
            if tag == 'span':
                if self._setting_fg_color:
                    self._set_fg_color_default()
                if self._setting_bg_color:  # no elif, could be multiple
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
                self.tokens.append(make_hyperlink(*self.anchor, icon='🔗'))
                self._set_fg_color_default()
                self.anchor = None

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

            elif tag == 'p':
                self._new_paragraph()

            elif tag == 'q':
                self.tokens.append('”')


fg_cache = StringCache(fg)
bg_cache = StringCache(bg)
fx_cache = StringCache(fx, em='i', h1='b,u', h2='b', h3='i', strong='b')
# disables individual styles:
dx_cache = StringCache(defx, em='i', h1='b,u', h2='b', h3='i', strong='b')
parser = LiteHTMLParser()


def hprint(*args, **kwargs):
    ''' Print function for terminals with limited HTML support. '''
    end = kwargs.pop('end', None)

    for arg in args:
        result = ''
        if isinstance(arg, str) and '<' in arg:
            parser.feed(arg)
            result = ''.join(parser.tokens)
            parser.tokens.clear()
        else:
            result = arg

        debug('called with: %r %s', result, kwargs)
        print(result, end='', **kwargs)
    print(end=end)


if __name__ == '__main__':

    import sys

    if '-d' in sys.argv:
        try:
            import out
            out.configure(level='debug')
        except ImportError:
            logging.basicConfig(level='DEBUG',
                format=f'%(levelname)s {fx.dim}%(funcName)s:{fg.green}%(lineno)s{fg.default}{defx.dim} %(message)s'
            )

    #~ <!--
    #~ -->
    html = '''
    <h1>HTML Print Test:</h1>
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
    <c #b0b>B0B</c> -&gt; <a href="http://example.com/">click here!</a>
    <p>
    A bit of <q>plain text</q> in its own paragraph.</p>
    <!-- nothing in this comment should be shown -->
    Hello <h2>world!</h2> ;-)
    '''
    hprint(html)
