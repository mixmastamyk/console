'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2020, Mike Miller - Released under the LGPL, version 3+.

    This module contains an HTML to ANSI sequence printer.
'''
import logging

from console import fg, bg, fx, defx
from console.utils import make_hyperlink

from html.parser import HTMLParser


log = logging.getLogger(__name__)
debug = log.debug
fx_tags = ('b', 'i', 's', 'u', 'em', 'h1', 'h2', 'h3', )


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
        val = str(getattr(self._palette, key))  # render palette entry
        self[key] = val
        #~ debug('missing called with: %r, returned %r', key, val)
        return val

import re
whitespace = re.compile(r'\s+')

class LiteHTMLParser(HTMLParser):
    ''' Parses simple HTML tags, returns as text and ANSI sequences. '''
    anchor = []
    tokens = []
    setting_bg_color = False
    setting_fg_color = False

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
            if data.startswith('\n'):  # at the end of each line
                data = data.lstrip()
                if tokens and not tokens[-1].endswith('\n'):  # breathing room
                    data = ' ' + data
                if not data:
                    return
                debug('data1: %r', data)

            # consolidate remaining whitespace to a single space:
            data = whitespace.sub(' ', data)
            tokens.append(data)
        debug('tokens: %r\n', self.tokens)

    def _set_fg_color(self, val):
        self.tokens.append(fg_cache[val])
        self.setting_fg_color = True

    def _set_bg_color(self, val):
        self.tokens.append(bg_cache[val])
        self.setting_bg_color = True

    def _set_fg_color_default(self):
        self.tokens.append(fg_cache['default'])
        self.setting_fg_color = False

    def _set_bg_color_default(self):
        self.tokens.append(bg_cache['default'])
        self.setting_bg_color = False

    def _new_paragraph(self, desc='start'):  # max two newlines at a time
        tokens = self.tokens
        debug('%s tokens0: %s', desc, tokens)
        if tokens:
            last = tokens[-1]
            if last.endswith('\n\n'):   # cap newlines at two
                pass
            elif last.endswith('\n'):   # ends with
                tokens.append('\n')
            else:
                tokens.append('\n\n')
        else:
            tokens.append('\n')
        debug('%s tokens1: %s', desc, tokens)

    def handle_starttag(self, tag, attrs):
        debug('start tag: %s', tag)
        if tag in fx_tags:
            if tag.startswith('h'):
                self._new_paragraph()
            self.tokens.append(fx_cache[tag])
        else:
            if tag == 'span':
                for key, val in attrs:
                    if key == 'style':
                        for pair in val.split(';'):
                            prop, _, v2 = [
                                x.strip() for x in pair.partition(':')
                            ]
                            if prop == 'color':
                                self._set_fg_color(v2)
                            elif prop in ('background', 'background-color'):
                                self._set_bg_color(v2)
            elif tag == 'c':
                fore = True
                for key, val in attrs:
                    if key == 'on':
                        fore = False; continue
                    if fore:
                        self._set_fg_color(key)  # <-- not val!
                    else:
                        self._set_bg_color(key)  # <-- not val!

            elif tag == 'a':
                for key, val in attrs:
                    if key == 'href':
                        self.anchor.append(val)  # target

            elif tag == 'br':
                self.tokens.append('\n')

            elif tag == 'p':
                self._new_paragraph()

            elif tag == 'font':
                for key, val in attrs:
                    if key == 'color':
                        self._set_fg_color(val)

    def handle_endtag(self, tag):
        debug('end tag: %s', tag)
        if tag in fx_tags:
            self.tokens.append(dx_cache[tag])
            if tag.startswith('h'):
                self._new_paragraph(desc='  end')
        else:
            if tag == 'span':
                if self.setting_fg_color:
                    self._set_fg_color_default()
                if self.setting_bg_color:  # no elif, could be multiple
                    self._set_bg_color_default()

            elif tag == 'font':
                if self.setting_fg_color:
                    self._set_fg_color_default()

            elif tag == 'c':
                if self.setting_fg_color:
                    self._set_fg_color_default()
                if self.setting_bg_color:  # no elif, could be multiple
                    self._set_bg_color_default()

            elif tag == 'p':
                self._new_paragraph()

            elif tag == 'a':
                self._set_fg_color('lightblue')
                self.tokens.append(make_hyperlink(*self.anchor))
                self._set_fg_color_default()
                self.anchor = None


fg_cache = StringCache(fg)
bg_cache = StringCache(bg)
fx_cache = StringCache(fx, em='i', h1='b', h2='b', h3='i')
# disables individual styles:
dx_cache = StringCache(defx, em='i', h1='b', h2='b', h3='i')
parser = LiteHTMLParser()


def hprint(*args, **kwargs):
    ''' Print function for terminals with limited HTML support. '''
    end = kwargs.pop('end', '')

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
                format='%(levelname)s %(funcName)s:%(lineno)s %(message)s'
            )

    html = '''
    <h1>HTML Print Test:</h1>
    <b>bold</b> <i>italic</i><em>/em</em> <s>strike</s> <u>undy</u><br>
    foo <i>(span tag)</i>
    To<span style="color: red">Bill</span> Brasky!
    To <span style="color: red">Bill</span>Brasky!
    <b><span style=background:green>gr&euro;&euro;n</span></b>
      <i>(w/ entities)</i>
    <span style="color: cyan">cyan</span>
    <span style="background: yellow; color: black">yellow</span>
    <span style="color: #444">#444</span> <i>(web/hex colors)</i><br>
    <i>(font tag)</i>
    <font color=blue>blue </font> <font color=purple> purple</font><br>
    <i>(c/color tag, web/X11 color names)</i>
    <c orange>l'orange</c>
    <c black on bisque3>bisque3</c>
    <c #b0b>B0B</c> -&gt; <a href="http://example.com/">click here!</a><p>
    A bit of text in its own paragraph.</p>
    <!-- comments should not be seen, correct? -->
    '''
    #~ <!--
    #~ -->
    hprint(html)

