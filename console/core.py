# -*- coding: future_fstrings -*-
'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    Complicated gobbyldegook supporting simple user interfaces located here.

    Classes below not meant to be instantiated by client code.
'''
import sys
import logging
import re

from . import _CHOSEN_PALETTE
from .constants import (CSI, ANSI_BG_LO_BASE, ANSI_BG_HI_BASE, ANSI_FG_LO_BASE,
                        ANSI_FG_HI_BASE, ANSI_RESET)
from .disabled import empty_bin, empty
from .detection import get_available_palettes, is_fbterm
from .meta import defaults
from .proximity import (color_table4, find_nearest_color_hexstr,
                        find_nearest_color_index)

try:
    import webcolors
except ImportError:
    webcolors = None


log = logging.getLogger(__name__)
MAX_NL_SEARCH = defaults.MAX_NL_SEARCH
string_plus_call_warning = '''

    Potentially inefficient or problematic construct:
        Form:  pal.style1 + pal.style2(msg)
        Given: %r + %r

    Suggested alternatives:
        (pal.style1 + pal.style2)(msg)  # new anonymous style
    Or:
        pal.style2(msg, pal.style1)     # via "mixins"
'''

# Palette attribute name finders, now we've got two problems.
# Not a huge fan of regex but here they nicely enforce the naming rules:
_hd = r'[0-9A-Fa-f]'  # hex digits
_index_finder = re.compile(r'^i_?\d{1,3}$', re.A)                   # i_DDD
_nearest_finder = re.compile(f'^n_?{_hd}{{3}}$', re.A)              # n_HHH
_true_finder = re.compile(f'^t_?({_hd}{{3}}|{_hd}{{6}})$', re.A)    # t_HHH+
_x11_finder = re.compile(r'^x\w{4,64}$', re.A)                      # x_NAME
_web_finder = re.compile(r'^w\w{4,64}$', re.A)                      # x_NAME


class _BasicPaletteBuilder:
    ''' Code container for ANSI colors, styles, fonts, etc.

        A container object base-class that creates child attributes on
        initialization.  Attributes are ANSI codes as integers wrapped in a
        manager object to provide additional functionality.

        Basic is useful for the basic 8/16 color and fx palettes.
    '''
    def __new__(cls, palettes=Ellipsis):
        ''' Override new() to replace the class entirely on deactivation.

            Arguments:
                palettes    - The palette(s) to support, e.g. from:
                              ('basic', 'extended', 'truecolor').

                              - Set explicitly with: str or sequence,
                              - Disable with: None
                              - Ellipsis - Autodetect environment.
        '''
        self = super().__new__(cls)
        if palettes is Ellipsis:                # autodetecten-Sie
            if _CHOSEN_PALETTE:  # enable "up to" the chosen palette level:
                palettes = get_available_palettes(_CHOSEN_PALETTE)
            else:
                self = empty_bin                # None, deactivate
                palettes = ()                   # skipen-Sie bitte
        elif type(palettes) in (list, tuple):   # carry on fine sir
            pass
        elif type(palettes) is str:             # make iterable
            palettes = (palettes,)
        elif palettes is None:                  # Ah, Shaddap-a ya face
            self = empty_bin
            palettes = ()                       # skipen-Sie
        else:
            raise TypeError(f'{palettes!r} was unrecognized.')

        self._palette_support = palettes
        return self

    def __init__(self, **kwargs):
        # look for integer attributes to wrap as a basic palette:
        for name in ['default'] + dir(self):        # default needs to go 1st!
            if not name.startswith('_'):
                value = getattr(self, name)
                if type(value) is int:
                    if 'basic' in self._palette_support:
                        attr = _PaletteEntry(self, name.upper(), value)
                    else:
                        attr = empty
                    setattr(self, name, attr)

    def __repr__(self):
        return f'{self.__class__.__name__}(palettes={self._palette_support})'


class _HighColorPaletteBuilder(_BasicPaletteBuilder):
    ''' Container/Router for ANSI Extended & Truecolor palettes.

        Unlike the Basic palette builder, this one computes attributes on the
        fly.
    '''
    def __init__(self, downgrade_method='euclid', **kwargs):
        super().__init__(**kwargs)

        self._dg_method = downgrade_method

    def __getattr__(self, name):
        ''' Traffic cop - called only when an attribute is missing,
            i.e. once per palette entry attribute.

            The "basic" palette attributes will never get here,
            as they are already defined.  Data flow:

            Prefixes:                               Examples:

                - t_ hex-string:                    'bb00bb'
                - x_ name to tuple of dec-int str:  ('1', '2', '3')
                - w_ name to tuple of int8:         (1, 2, 3)

            On downgrade, find nearest:

                 - Prefer tuple of int8:            (1, 2, 3)
                 - Also handles 3 digit hex-string: 'b0b'

                - returns: integer index
                    * 0-15 or
                    * 0-255

            Output:

                - String index from int index:      '30'
                - Tuple of dec-int strings:         ('1', '2', '3')
                    - joined with ';' to string:    Prefix + '1;2;3'

            Final Output:
                - wrap in _PaletteEntry(output)
        '''
        key = name[1:].lstrip('_')  # rm potential prefix
        result = None

        # follow the yellow brick road…
        if _index_finder.match(name):       # Indexed aka Extended
            result = self._get_extended_palette_entry(name, key)

        elif _nearest_finder.match(name):   # Nearest
            result = self._get_extended_palette_entry(name, key, is_hex=True)

        elif _true_finder.match(name):      # Truecolor
            result = self._get_true_palette_entry(name, key)

        elif _x11_finder.match(name):       # X11, forced via prefix
            result = self._get_X11_palette_entry(key)

        elif _web_finder.match(name):       # Webcolors, forced via prefix
            result = self._get_web_palette_entry(key)

        else:  # look for bare names (without prefix)
            try:
                result = self._get_web_palette_entry(name)
                if result:
                    return result
            except AttributeError:
                pass  # nope, didn't find…

            try:  # try X11
                result = self._get_X11_palette_entry(name)
                if result:
                    return result
            except AttributeError:
                pass  # nada

            # Emerald city
            raise AttributeError(f'{name!r} is not a recognized attribute name'
                                 ' or format.')
        return result

    def _get_extended_palette_entry(self, name, index, is_hex=False):
        ''' Compute extended entry, once on the fly. '''
        values = None

        if 'extended' in self._palette_support:  # build entry
            if is_hex:
                index = str(find_nearest_color_hexstr(index,
                                                      method=self._dg_method))
            start_codes = self._start_codes_extended
            if is_fbterm:
                start_codes = self._start_codes_extended_fbterm

            values = [start_codes, index]

        # downgrade section
        elif 'basic' in self._palette_support:
            if is_hex:
                nearest_idx = find_nearest_color_hexstr(index, color_table4,
                                                        method=self._dg_method)
            else:
                from .color_tables import index_to_rgb8  # find rgb for idx
                nearest_idx = find_nearest_color_index(*index_to_rgb8[index],
                                                       color_table=color_table4,
                                                       method=self._dg_method)
            values = self._index_to_ansi_values(nearest_idx)

        return (self._create_entry(name, values) if values else empty)

    def _get_true_palette_entry(self, name, digits):
        ''' Compute truecolor entry, once on the fly.

            values must become sequence of decimal int strings: ('1', '2', '3')
        '''
        values = None
        type_digits = type(digits)

        if 'truecolor' in self._palette_support:  # build entry
            values = [self._start_codes_true]
            if type_digits is str:  # convert from hex string
                if len(digits) == 3:
                    values.extend(str(int(ch + ch, 16)) for ch in digits)
                else:  # chunk 'BB00BB', to ints to 'R', 'G', 'B':
                    values.extend(str(int(digits[i:i+2], 16)) for i in (0, 2 ,4))
            else:  # tuple of str-digit or int from webcolors
                values.extend(str(digit) for digit in digits)

        # downgrade section
        elif 'extended' in self._palette_support:
            if type_digits is str:
                nearest_idx = find_nearest_color_hexstr(digits,
                                                       method=self._dg_method)
            else:  # tuple
                if type(digits[0]) is str:  # convert to ints
                    digits = tuple(int(digit) for digit in digits)
                nearest_idx = find_nearest_color_index(*digits,
                                                       method=self._dg_method)

            start_codes = self._start_codes_extended
            if is_fbterm:
                start_codes = self._start_codes_extended_fbterm

            values = [start_codes, str(nearest_idx)]

        elif 'basic' in self._palette_support:
            if type_digits is str:
                nearest_idx = find_nearest_color_hexstr(digits, color_table4,
                                                       method=self._dg_method)
            else:  # tuple
                if type(digits[0]) is str:  # convert to ints
                    digits = tuple(int(digit) for digit in digits)
                nearest_idx = find_nearest_color_index(*digits,
                                                       color_table=color_table4,
                                                       method=self._dg_method)
            values = self._index_to_ansi_values(nearest_idx)

        return (self._create_entry(name, values) if values else empty)

    def _get_X11_palette_entry(self, name):
        from .color_tables import x11_color_map
        result = empty

        try:            # decimal int strings, e.g.: ('1', '2', '3')
            color = x11_color_map[name.lower()]
        except KeyError:  # convert to AttributeError
            raise AttributeError(f'{name.lower()!r} not found in X11 palette.')
        result = self._get_true_palette_entry(name, color)
        return result

    def _get_web_palette_entry(self, name):
        result = empty
        if webcolors:
            try:  # wc: returns tuple of "decimal" int: (1, 2, 3)
                color = webcolors.name_to_rgb(name)
                result = self._get_true_palette_entry(name, color)
            except ValueError:  # convert to AttributeError
                raise AttributeError(
                    f'{name!r} not found in webcolors palette.')
        return result

    def _create_entry(self, name, values):
        ''' Render first values as string and place as first code,
            save, and return attr.
        '''
        str_values = ';'.join(values)
        if is_fbterm:
            attr = _PaletteEntryFBTerm(self, name.upper(), str_values)
        else:
            attr = _PaletteEntry(self, name.upper(), str_values)
        setattr(self, name, attr)  # now cached
        return attr

    def _index_to_ansi_values(self, index):
        ''' Converts a palette index to the corresponding ANSI color.

            Arguments:
                index   - an int (from 0-15)
            Returns:
                index as str in a list for compatibility with values.
        '''
        if self.__class__.__name__[0] == 'F':   # Foreground
            if index < 8:
                index += ANSI_FG_LO_BASE
            else:
                index += (ANSI_FG_HI_BASE - 8)  # 82
        else:                                   # Background
            if index < 8:
                index += ANSI_BG_LO_BASE
            else:
                index += (ANSI_BG_HI_BASE - 8)  # 92
        return [str(index)]

    def clear(self):
        ''' Cleanse the palette to free memory.
            Useful for truecolor, perhaps.
        '''
        self.__dict__.clear()


class _LineWriter(object):
    ''' Writes each line with escape sequences terminated so paging works
        correctly, a la Pygments.
    '''
    def __init__(self, start, stream, default):
        self.start = start
        self.stream = stream
        self.default = default

    def write(self, data):
        ''' This could be a bit less clumsy. '''
        if data == '\n':  # print does this
            return self.stream.write(data)
        else:
            bytes_written = 0
            for line in data.splitlines(True):
                nl = ''
                if line.endswith('\n'):  # mv nl to end:
                    line = line[:-1]
                    nl = '\n'
                bytes_written += self.stream.write(
                                    f'{self.start}{line}{self.default}{nl}'
                                 ) or 0  # in case None returned (on Windows)
            return bytes_written

    def __getattr__(self, attr):
         return getattr(self.stream, attr)


class _PaletteEntry:
    ''' Palette Entry Attribute

        Enables:

        - Rendering to an escape sequence string.
        - Addition of attributes, to create a combined, single sequence.
        - Provides a call interface, for use as a text wrapper.
        - Provides a Context Manager for use via the "with" statement.

        Arguments:
            parent  - Parent palette
            name    - Display name, used in demos.
            code    - Associated ANSI code number.
            stream  - Stream to print to, when using a context manager.
    '''
    def __init__(self, parent, name, code, stream=sys.stdout):
        self.parent = parent
        self.default = (parent.default if hasattr(parent, 'default')
                                       else parent.end)  # style
        self.name = name
        self._codes = [str(code)]           # the initial code
        self._stream = stream               # for redirection

    def __add__(self, other):
        ''' Add: self + other '''
        if isinstance(other, str):
            if other.startswith(CSI) and other.endswith('m'):
                # TODO: this could be handled slightly better by splitting the
                #       string on newlines and splicing the new style into
                #       non-default ansi sequences.
                import warnings
                msg = string_plus_call_warning % (self, other)
                warnings.warn(msg)
                log.debug(msg)
            return str(self) + other

        elif isinstance(other, _PaletteEntry):
            # Make a copy, so codes don't pile up after each addition
            # Render initial values once as string and place as first code:
            newcodes = self._codes + other._codes
            attr = _PaletteEntry(self.parent, self.name,
                                 ';'.join(newcodes))
            same_category = self.parent is other.parent  # color or style

            if not same_category:  # different, use instead of color default
                attr.default = ANSI_RESET

            return attr
        else:
            raise TypeError(f'Addition to type {type(other)} not supported.')

    def __radd__(self, other):
        ''' Reverse add: other + self '''
        return other + str(self)

    def __bool__(self):
        return bool(self._codes)

    def __enter__(self):
        ''' Wrap output streams. '''
        log.debug(repr(str(self)))
        # wrap originals
        self._orig_stdout = sys.stdout
        sys.stdout = _LineWriter(self, self._stream, self.default)
        return sys.stdout

    def __exit__(self, type, value, traceback):
        sys.stdout = sys.stdout.stream
        self._stream.write(str(self.default))  # just in case

    def __call__(self, text, *styles, original_length=False):
        ''' Formats text.  Not appropriate for huge input strings.

            Arguments:
                text                Original text.
                *styles             Add "mix-in" styles, per invocation.
                original_length     bool - Save original string length for
                                    later use.

            Note:
                Color sequences are terminated at newlines,
                so that paging the output works correctly.
        '''
        if not text:  # when an empty string is passed, don't emit codes.
            return ''

        # if the category of styles is different,
        # copy uses fx.end instead of palette.default, see addition:
        for attr in styles:
            self += attr

        pos = text.find('\n', 0, MAX_NL_SEARCH)  # if '\n' in text, w/limit
        if pos != -1:  # found
            lines = text.splitlines()
            for i, line in enumerate(lines):
                lines[i] = f'{self}{line}{self.default}'  # add styles, see tip
            result = '\n'.join(lines)
        else:
            result = f'{self}{text}{self.default}'

        if original_length:
            return _LengthyString(len(text), result)
        else:
            return result

    def __str__(self):
        return f'{CSI}{";".join(self._codes)}m'

    def __repr__(self):
        return repr(self.__str__())

    def template(self, placeholder='{}'):
        ''' Returns a template string from this Entry with its attributes.

            Placeholder can be '%s', '{}', '${}' or other depending on your
            needs.
        '''
        return f'{self}{placeholder}{self.default}'

    def set_output(self, outfile):
        ''' Set's the output file, currently only useful with context-managers.

            Note:
                This function is experimental and may not last.
        '''
        if self._orig_stdout:  # restore Usted
            sys.stdout = self._orig_stdout

        self._stream = outfile
        sys.stdout = _LineWriter(self, self._stream, self.default)


class _PaletteEntryFBTerm(_PaletteEntry):
    ''' Help fbterm show 256 colors. '''
    def __str__(self):
        return f'{CSI}{";".join(self._codes)}}}'  # note '}' at end not std 'm'


class _LengthyString(str):
    ''' String that returns the length of its bare string, before escape
        sequences were added.
    '''
    def __new__(cls, original_length, content):
        self = str.__new__(cls, content)
        self.original_length = original_length
        return self
