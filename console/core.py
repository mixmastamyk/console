# -*- coding: future_fstrings -*-
'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    Complicated gobbyldegook supporting the simple color/style interface
    located here.
    Classes below are not meant to be instantiated by client code;
    see style.py.
'''
import sys
import logging
import re

from . import term_level as _term_level
from .constants import (CSI, ANSI_BG_LO_BASE, ANSI_FG_LO_BASE, ANSI_RESET,
                        TermLevel)
from .disabled import empty_bin, empty
from .detection import is_fbterm, color_sep
from .meta import defaults
from .proximity import (color_table4, find_nearest_color_hexstr,
                        find_nearest_color_index)

try:
    import webcolors
except ImportError:
    webcolors = None


log = logging.getLogger(__name__)
MAX_NL_SEARCH = defaults.MAX_NL_SEARCH
_string_plus_call_warning_template = '''

    Ambiguous and/or inefficient addition operation used:
        Form:  pal.style1 + pal.style2(msg)
          or:  adding a style to a previously ANSI escaped string.
        Given: %r + %r

    Suggested alternatives:
        (pal.style1 + pal.style2)(msg)  # new anonymous style
    Or:
        pal.style2(msg, pal.style1)     # via "mixins"
'''

# Palette attribute name finders.  Now we've got two problems.
# Not a huge fan of regex but they nicely enforce the attribute naming rules:
_hd = '[0-9A-Fa-f]'  # hex digits
_index_finder = re.compile(r'^i_?\d{1,3}$', re.A)                   # i_DDD
_nearest_finder = re.compile(f'^n_?{_hd}{{3}}$', re.A)              # n_HHH
_true_finder = re.compile(f'^t_?({_hd}{{3}}|{_hd}{{6}})$', re.A)    # t_HHH+
_x11_finder = re.compile(r'^x_\w{4,64}$', re.A)                     # x_NAME
_web_finder = re.compile(r'^w_\w{4,64}$', re.A)                     # w_NAME


class _BasicPaletteBuilder:
    ''' Code container for ANSI colors and effects.

        A container base-class that creates child attributes on initialization.
        Attributes are integer ANSI codes that are wrapped in a _PaletteEntry
        object to provide functionality.

        Used for the basic 8/16 color and fx palettes.
    '''
    def __new__(cls, color_sep=None, level=Ellipsis):
        ''' Override new() to replace the class entirely on deactivation.

            Arguments:
                level       - Term level to support.
                              - Ellipsis - Detect from environment.
        '''
        self = super().__new__(cls)
        self._level = TermLevel.DUMB

        if level is Ellipsis:                   # autodetecten-Sie
            if _term_level:
                self._level = _term_level
            else:  # None
                self = empty_bin                # deactivate self
        elif isinstance(level, TermLevel):      # continue on fine sir…
            self._level = level
        elif level is None:                     # Ah, Shaddap-a ya face
            self = empty_bin
        else:
            raise TypeError(f'level: {level!r} was unrecognized.')

        return self

    def __init__(self, color_sep=color_sep, **kwargs):
        # look for attributes to wrap as a basic palette:
        attributes = ['default'] + dir(self)  # default needs to go first
        color_available = self._level >= TermLevel.ANSI_BASIC  # look again
        mono_available = color_available or (
            isinstance(self, _MonochromePaletteBuilder) and
            self._level >= TermLevel.ANSI_MONOCHROME
        )
        for name in attributes:
            if not name.startswith('_'):
                value = getattr(self, name, None)  # fx has no default
                if type(value) in (int, str, tuple):  # skip methods, default²
                    if color_available or mono_available:
                        attr = _PaletteEntry(self, name.upper(), value)
                    else:
                        attr = empty
                    setattr(self, name, attr)

        self._color_sep = color_sep  # for ease of testing

    def __repr__(self):
        return f'{self.__class__.__name__}(level={self._level.name})'


class _MonochromePaletteBuilder(_BasicPaletteBuilder):
    ''' A type of PaletteBuilder that let's us classify and enable effects
        objects.
    '''
    pass


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
            i.e. once per palette entry attribute.  The "basic" palette
            attributes will never get here, as they are already defined.

            Data flow: look up the name by its prefix (or not), then convert to
            a RGB three-tuple, for optional calculation and output.

            Attribute prefixes:                     Examples:

                - t_ hex-string:                    .t_bb00bb
                - x_ name:                          .x_lime
                - w_ name to tuple of int8:         .w_bisque
                - Bare names                        .cornflowerblue

            Convert to three-tuples:
                (1, 2, 3) or ('1', '2', '3')

            On downgrade, find nearest:

                 - Prefer tuple of ints:            (1, 2, 3)
                 - Also handles 3 digit hex-string: 'b0b'

                - returns: integer index
                    * 0-15 or
                    * 0-255

            Output, one of:

                - String index from integer:        '30'
                - Tuple of dec-int strings:         ('1', '2', '3')
                    - joined with ';' to string:    Prefix + '1;2;3'

            Final Output:
                - wrap in _PaletteEntry(output)
        '''
        key = name[1:].lstrip('_')  # rm prefix from key
        result = None

        # follow the yellow brick road…
        if _index_finder.match(name):       # Indexed aka Extended
            result = self._get_extended_palette_entry(name, key)

        elif _nearest_finder.match(name):   # Nearest index
            result = self._get_extended_palette_entry(name, key, is_hex=True)

        elif _true_finder.match(name):      # Direct color
            result = self._get_direct_palette_entry(name, key)

        elif _x11_finder.match(name):       # X11, forced via prefix
            result = self._get_X11_palette_entry(key)

        elif _web_finder.match(name):       # Webcolors, forced via prefix
            result = self._get_web_palette_entry(key)

        else:  # look for bare names (without prefix)
            if webcolors:
                try:
                    return self._get_web_palette_entry(name)
                except AttributeError:
                    pass  # nope, didn't find…

            try:  # try X11
                result = self._get_X11_palette_entry(name)
                if result:
                    return result
            except AttributeError:
                pass  # nada

            # Emerald city
            cname = self.__class__.__name__
            raise AttributeError(f'{cname} - {name!r} is not a recognized '
                                 'color name or format.')
        return result

    def _get_extended_palette_entry(self, name, index, is_hex=False):
        ''' Compute extended entry. '''
        values = []

        if self._level >= TermLevel.ANSI_EXTENDED:  # build entry
            if is_hex:
                index = str(find_nearest_color_hexstr(index,
                                                      method=self._dg_method))
            start_codes = self._start_codes_extended
            if is_fbterm:
                start_codes = self._start_codes_extended_fbterm
            values.extend(start_codes)  # no colorspace param needed
            values.append(index)

        # downgrade section
        elif self._level is TermLevel.ANSI_BASIC:
            if is_hex:
                nearest_idx = find_nearest_color_hexstr(index, color_table4,
                                                        method=self._dg_method)
            else:
                from .color_tables import index_to_rgb8  # find rgb for idx
                nearest_idx = find_nearest_color_index(*index_to_rgb8[index],
                                                       color_table=color_table4,
                                                       method=self._dg_method)
            values.extend(self._index_to_ansi_values(nearest_idx))

        return (self._create_entry(name, values) if values else empty)

    def _get_direct_palette_entry(self, name, digits):
        ''' Compute direct color entry.

            Values become sequence of decimal int strings: ('1', '2', '3')
        '''
        values = []
        digits_type = type(digits)

        if self._level >= TermLevel.ANSI_DIRECT:  # build entry
            values.extend(self._start_codes_direct)
            if self._color_sep == ':':
                values.append('')  # needs a colorspace param, ok if empty
            if digits_type is str:  # convert from hex string
                if len(digits) == 3:
                    values.extend(str(int(ch + ch, 16)) for ch in digits)
                else:  # chunk 'BB00BB', to ints to 'R', 'G', 'B':
                    values.extend(str(int(digits[i:i+2], 16)) for i in (0, 2 ,4))
            else:  # tuple of str-digit or int from webcolors
                values.extend(str(digit) for digit in digits)

        # downgrade section
        elif self._level is TermLevel.ANSI_EXTENDED:  # build entry
            start_codes = self._start_codes_extended
            if is_fbterm:
                start_codes = self._start_codes_extended_fbterm

            if digits_type is str:
                nearest_idx = find_nearest_color_hexstr(digits,
                                                        method=self._dg_method)
            else:  # tuple
                if type(digits[0]) is str:  # convert to ints
                    digits = tuple(int(digit) for digit in digits)
                nearest_idx = find_nearest_color_index(*digits,
                                                       method=self._dg_method)
            values.extend(start_codes)
            values.append(str(nearest_idx))

        elif self._level is TermLevel.ANSI_BASIC:
            if digits_type is str:
                nearest_idx = find_nearest_color_hexstr(digits, color_table4,
                                                       method=self._dg_method)
            else:  # tuple
                if type(digits[0]) is str:  # convert to ints
                    digits = tuple(int(digit) for digit in digits)
                nearest_idx = find_nearest_color_index(*digits,
                                                       color_table=color_table4,
                                                       method=self._dg_method)
            values.extend(self._index_to_ansi_values(nearest_idx))

        return (self._create_entry(name, values) if values else empty)

    def _get_X11_palette_entry(self, name):
        ''' Look up colors from bundled X11 palette. '''
        from .color_tables_x11 import x11_color_map
        result = empty
        try:            # to decimal int strings, e.g.: ('1', '2', '3')
            color = x11_color_map[name.lower()]
        except KeyError:  # convert to AttributeError
            raise AttributeError(f'{name.lower()!r} not found in X11 palette.')
        result = self._get_direct_palette_entry(name, color)
        return result

    def _get_web_palette_entry(self, name):
        ''' Look up colors from webcolors module. '''
        result = None
        try:  # wc: returns tuple of "decimal" int: (1, 2, 3)
            color = webcolors.name_to_rgb(name)
            result = self._get_direct_palette_entry(name, color)
        except (ValueError, AttributeError):  # convert to AttributeError
            raise AttributeError(
                f'{name!r} not found in webcolors palette.')
        return result

    def _create_entry(self, name, values):
        ''' Render first values as string and place as first code,
            save, and return attr.
        '''
        if is_fbterm:
            str_values = ';'.join(values)  # always semi-colon
            attr = _PaletteEntryFBTerm(self, name.upper(), str_values)
        else:
            str_values = self._color_sep.join(values)
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
                index += 82                     # (ANSI_FG_HI_BASE - 8)
        else:                                   # Background
            if index < 8:
                index += ANSI_BG_LO_BASE
            else:
                index += 92                     # (ANSI_BG_HI_BASE - 8)
        return [str(index)]

    def _clear(self):
        ''' "Cleanse the palette" to free memory.
            Useful for direct color, perhaps.
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
            for line in data.splitlines(True):  # keep ends: True
                end = ''
                if line.endswith('\n'):  # mv nl to end:
                    line = line[:-1]
                    end = '\n'
                bytes_written += self.stream.write(
                                    f'{self.start}{line}{self.default}{end}'
                                 ) or 0  # in case None returned (on Windows)
            return bytes_written

    def __getattr__(self, attr):
         return getattr(self.stream, attr)


class _PaletteEntry:
    ''' Palette Entry Attribute, a.k.a. a "color"

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
    _end_code = 'm'

    def __init__(self, parent, name, code, stream=sys.stdout):
        self._parent = parent
        self.name = name
        self._stream = stream               # for redirection

        # find initial code and default
        default = None
        if type(code) in (int, str):
            self._codes = [str(code)]
        elif type(code) is tuple:
            self._codes = [str(code[0])]
            default = f'{CSI}{code[1]}m'    # pre-render
        else:
            TypeError('code not valid: %r' % code)

        self.default = default or (parent.default if hasattr(parent, 'default')
                                                  else parent.end)  # style

    def __add__(self, other):
        ''' Add: self + other '''
        if isinstance(other, str):
            if other.startswith(CSI) and other.endswith(self._end_code):
                return self._handle_ambiguous_op(other)
            else:
                return str(self) + other

        elif type(other) is _PaletteEntryFBTerm:  # not! isinstance
            return _CallableFBString(str(self) + str(other))

        elif isinstance(other, _PaletteEntry):
            # Make a copy, so codes don't pile up after each addition
            # Render initial values once as string and place as first code:
            newcodes = self._codes + other._codes
            new_entry = _PaletteEntry(self._parent, self.name,
                                      ';'.join(newcodes))   # _not_ color_sep
                                                            # different type
            if not self.default == other.default:   # not in same class,
                new_entry.default = ANSI_RESET      # switch to full reset

            return new_entry
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
        log.debug(repr(str(self.default)))
        self._stream.write(str(self.default))  # just in case

    def __call__(self, text, *styles, save_length=False):
        ''' Formats text.  Not appropriate for *huge* input strings.

            Arguments:
                text                Original text.
                *styles             Add "mix-in" styles, per invocation.
                save_length         bool - Save original string length for
                                    later use.

            Note:
                Color sequences are terminated at newlines,
                so that paging of output works correctly.
        '''
        if (self._parent.__class__.__name__ == 'EffectsTerminator' or
            self.name in ('DEFAULT', 'END')):
            raise NotImplementedError("call form undefined for "
                                      "EffectsTerminator or 'default'.")
        if not text:  # when an empty string/None is passed, don't emit codes.
            return ''

        # if the defaults of mixins are different,
        # uses fx.end instead of palette.default, see addition:
        for attr in styles:
            self += attr

        # add and end styles per line, to facilitate paging:
        pos = text.find('\n', 0, MAX_NL_SEARCH)  # if '\n' in text, w/limit
        if pos == -1:  # not found
            result = f'{self}{text}{self.default}'
        else:
            lines = text.splitlines()
            for i, line in enumerate(lines):
                lines[i] = f'{self}{line}{self.default}'  # add styles, see tip
            result = '\n'.join(lines)

        if save_length:
            return _LengthyString(len(text), result)
        else:
            return result

    def __str__(self):
        return f'{CSI}{";".join(self._codes)}m'  # not color_sep, styles also

    def __repr__(self):
        return repr(self.__str__())

    def _handle_ambiguous_op(self, other):
        ''' This operation is ambiguous and difficult to handle fully, e.g.::

                pal.style1 + pal.style2('hello')

            Attempts to break up the other ansi string by lines,
            insert codes into each opening sequence, conditionally fix end.
        '''
        import warnings

        msg = _string_plus_call_warning_template % (self, other)
        warnings.warn(msg, SyntaxWarning)  # warn first
        log.debug(msg)
        try:
            # do line by line to avoid doubling mem reqs
            lines = other.splitlines()
            for i, line in enumerate(lines):
                tokens = [CSI]
                tokens.append(';'.join(self._codes))            # if multiple
                tokens.append(';')
                tokens.append(CSI.join(line.split(CSI)[1:-1]))  # if multiple

                # figure end code:
                try:
                    end_code = self.default._codes[0]
                except AttributeError:  # already rendered
                    end_code = self.default.strip('\x1b[m')

                if end_code == other[-3:-1]:    # same category
                    tokens.append(str(self.default))
                else:                           # different
                    tokens.append(ANSI_RESET)
                # put humpty (pronounced with an -umpty) back together again:
                lines[i] = ''.join(tokens)
            result = '\n'.join(lines)

        except IndexError as err:
            log.warn('Could not perform enhanced addition with operands'
                     ': %r %r.  Falling back to str concatenation. %s',
                      self, other, err)
            result = str(self) + other

        return result

    def template(self, placeholder='{}'):
        ''' Returns a template string from this Entry with its attributes.

            Placeholder can be '%s', '{}', '${}' or other depending on your
            needs.
        '''
        return f'{self}{placeholder}{self.default}'

    def set_output(self, outfile):
        ''' Set's the output file, currently only useful with context-managers.

            Note:
                This function is experimental and may not survive.
        '''
        if self._orig_stdout:  # restore Usted
            sys.stdout = self._orig_stdout

        self._stream = outfile
        sys.stdout = _LineWriter(self, self._stream, self.default)


class _PaletteEntryFBTerm(_PaletteEntry):
    ''' Help fbterm show 256 colors. '''
    _end_code = '}'

    def __add__(self, other):
        ''' Add: self + other '''
        # these are not able to mix unfortunately, convert to callable string:
        if type(other) is _PaletteEntry:  # not! isinstance
            return _CallableFBString(str(self) + str(other))
        else:
            return super().__add__(other)

    def __str__(self):  # outer sep, not color_sep
        return f'{CSI}{";".join(self._codes)}}}'  # note '}' at end not std 'm'


class _CallableFBString(str):
    ''' String that is callable, only needed in the very specific instance of
        running under fbterm and combining extended color Palettes with other
        Palettes of a different category.  :-/
    '''
    def __call__(self, text, *styles, original_length=False):
        if not text:  # when an empty string/None is passed, don't emit codes.
            return ''

        # add and end styles per line, to facilitate paging:
        pos = text.find('\n', 0, MAX_NL_SEARCH)  # if '\n' in text, w/limit
        if pos == -1:  # not found
            result = f'{self}{text}{ANSI_RESET}'
        else:
            lines = text.splitlines()
            for i, line in enumerate(lines):
                lines[i] = f'{self}{line}{ANSI_RESET}'  # add styles, see tip
            result = '\n'.join(lines)
        return result


class _LengthyString(str):
    ''' String that saves and returns the length of its bare string, before
        escape sequences were added.
    '''
    def __new__(cls, original_length, content):
        self = str.__new__(cls, content)
        self.original_length = original_length
        return self
