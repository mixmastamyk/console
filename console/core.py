# -*- coding: future_fstrings -*-
'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    Complicated Gobbyldegook supporting simpler interfaces is located here.

    Classes below not meant to be instantiated by client code.
'''
import sys
import logging
import re

from . import _CHOSEN_PALETTE
from .constants import (CSI, ANSI_BG_LO_BASE, ANSI_BG_HI_BASE, ANSI_FG_LO_BASE,
                        ANSI_FG_HI_BASE, ANSI_RESET)
from .disabled import dummy, empty
from .detection import get_available_palettes
from .proximity import (color_table4, find_nearest_color_hexstr,
                        find_nearest_color_index)
try:
    import webcolors
except ImportError:
    webcolors = None


log = logging.getLogger(__name__)
MAX_NL_SEARCH = 4096

# Palette attribute name finders, now we've got two problems.
# Not a huge fan of regex but here they nicely enforce the naming rules:
_hd = r'[0-9A-Fa-f]'  # hex digits
_index_finder = re.compile(r'^i_?\d{1,3}$', re.A)                   # i_DDD
_nearest_finder = re.compile(f'^n_?{_hd}{{3}}$', re.A)              # n_HHH
_true_finder = re.compile(f'^t_?({_hd}{{3}}|{_hd}{{6}})$', re.A)    # t_HHH
_x11_finder = re.compile(r'^x\w{4,64}$', re.A)                      # x_NAME
_web_finder = re.compile(r'^w\w{4,64}$', re.A)                      # x_NAME

# X11 colors support
_x11_color_map = {}
X11_RGB_FILE = None  # Windows
if sys.platform == 'linux':
    X11_RGB_FILE = '/etc/X11/rgb.txt'
elif sys.platform == 'darwin':
    X11_RGB_FILE = '/opt/X11/share/X11/rgb.txt'


class _BasicPaletteBuilder:
    ''' ANSI code container for styles, fonts, etc.

        A base-class that modifies the attributes of child container classes on
        initialization.  Integer attributes are recognized as ANSI codes to be
        wrapped with a manager object to provide mucho additional
        functionality.  Useful for the basic 8/16 color/fx palettes.
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
        if palettes is Ellipsis:                # autodetecten-Sie
            if _CHOSEN_PALETTE:  # enable "up to" the chosen palette level:
                palettes = get_available_palettes(_CHOSEN_PALETTE)
            else:
                self = dummy                    # None, deactivate
                palettes = ()                   # skipen-Sie bitte
        elif type(palettes) in (list, tuple):   # carry on fine sir
            pass
        elif type(palettes) is str:             # make iterable
            palettes = (palettes,)
        elif palettes is None:                  # Ah, Shaddap-a ya face
            self = dummy
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
    ''' Container/Router for ANSI Extended & Truecolor palettes. '''

    def __init__(self, x11_rgb_filename=X11_RGB_FILE, **kwargs):
        super().__init__(**kwargs)
        self._x11_rgb_filename = x11_rgb_filename

    def __getattr__(self, name):
        ''' Traffic cop - called only when an attribute is missing,
            i.e. once per palette entry attribute.

            The "basic" palette will never get here, as it is already defined.
            Data flow:

            Input/lookup:                           Examples:

                - t_ hex-string:                    'bb00bb'
                - x_  tuple of dec-int strings:     ('1', '2', '3')
                - w_  tuple of "decimal" int:       (1, 2, 3)

            On downgrade, find nearest:

                 - Prefer tuple of int8:            (1, 2, 3)
                 - May handle 3 digit hex-string:   'b0b'

                - returns: integer index
                    * 0-15 or
                    * 0-255

            Output:

                - String index from int index:      '30'
                - tuple of dec-int strings:         ('1', '2', '3')
                    - joined with ';' to string:        Prefix + '1;2;3'

            Final Output:
                - wrap in _PaletteEntry(output)
        '''
        key = name[1:].lstrip('_')  # rm potential prefix
        result = None

        # follow the yellow brick road…
        if _index_finder.match(name):       # Indexed aka Extended
            result = self._get_extended_palette_entry(name, key)

        elif _nearest_finder.match(name):   # Nearest
            result = self._get_extended_palette_entry(name, key, ishex=True)

        elif _true_finder.match(name):      # Truecolor
            result = self._get_true_palette_entry(name, key)

        elif _x11_finder.match(name):       # X11, forced via prefix
            if not _x11_color_map:
                _load_x11_color_map(self._x11_rgb_filename)
            # x11 map: returns tuple of decimal int strings: ('1', '2', '3')
            result = self._get_true_palette_entry(name,
                                                  _x11_color_map[key.lower()])

        elif _web_finder.match(name):       # Webcolors, forced via prefix
            # wc: returns tuple of "decimal" int: (1, 2, 3)
            rgbs = webcolors.name_to_rgb(key)
            result = self._get_true_palette_entry(name, rgbs)

        else:  # look for bare names (without prefix)
            if webcolors:
                try:
                    rgbs = webcolors.name_to_rgb(name)
                    return self._get_true_palette_entry(name, rgbs)
                except ValueError:
                    pass  # didn't find…

            if X11_RGB_FILE:  # try X11
                try:
                    if not _x11_color_map:
                        _load_x11_color_map(self._x11_rgb_filename)
                    return self._get_true_palette_entry(
                                            name, _x11_color_map[key.lower()])
                except KeyError:
                    pass  # nope

            # Emerald city
            raise AttributeError(f'{name!r} is not a recognized attribute name'
                                 'or format.')
        return result

    def _get_extended_palette_entry(self, name, index, ishex=False):
        ''' Compute extended entry, once on the fly. '''
        values = None

        if 'extended' in self._palette_support:  # build entry
            if ishex:
                index = str(find_nearest_color_hexstr(index))
            values = [self._start_codes_extended, index]

        # downgrade section
        elif 'basic' in self._palette_support:
            if ishex:
                nearest_idx = find_nearest_color_hexstr(index, color_table4)
            else:
                from .color_tables import index_to_rgb8  # find rgb for idx
                nearest_idx = find_nearest_color_index(*index_to_rgb8[index],
                                                       color_table4)
            values = self._index_to_ansi_values(nearest_idx)

        return self._create_entry(name, values) if values else empty

    def _get_true_palette_entry(self, name, digits):
        ''' Compute truecolor entry, once on the fly.

            values must become sequence of decimal int strings: ('1', '2', '3')
        '''
        values = None
        type_digits = type(digits)

        if 'truecolor' in self._palette_support:  # build entry
            values = [self._start_codes_true]
            if type_digits is str:  # convert hex string
                if len(digits) == 3:
                    values.extend(str(int(ch + ch, 16)) for ch in digits)
                else:  # chunk 'BB00BB', to ints to 'R', 'G', 'B':
                    values.extend(str(int(digits[i:i+2], 16)) for i in (0, 2 ,4))
            else:  # tuple of str-digit or int, may not matter to bother:
                values.extend(str(digit) for digit in digits)

        # downgrade section
        elif 'extended' in self._palette_support:
            if type_digits is str:
                nearest_idx = find_nearest_color_hexstr(digits)
            else:  # tuple
                if type(digits[0]) is str:  # convert to ints
                    digits = tuple(int(digit) for digit in digits)
                nearest_idx = find_nearest_color_index(*digits)

            values = [self._start_codes_extended, str(nearest_idx)]

        elif 'basic' in self._palette_support:
            if type_digits is str:
                nearest_idx = find_nearest_color_hexstr(digits, color_table4)
            else:  # tuple
                if type(digits[0]) is str:  # convert to ints
                    digits = tuple(int(digit) for digit in digits)
                nearest_idx = find_nearest_color_index(*digits, color_table4)

            values = self._index_to_ansi_values(nearest_idx)

        return self._create_entry(name, values) if values else empty

    def _index_to_ansi_values(self, index):
        ''' Converts an palette index to the corresponding ANSI color.

            Arguments:
                index   - an int (from 0-15)
            Returns:
                index as str in a list for compatibility with values.
        '''
        if self.__class__.__name__[0] == 'F':   # Foreground
            if index < 8:
                index += ANSI_FG_LO_BASE
            else:
                index += (ANSI_FG_HI_BASE - 8)  # 82
        else:                                   # Background
            if index < 8:
                index += ANSI_BG_LO_BASE
            else:
                index += (ANSI_BG_HI_BASE - 8)  # 92
        return [str(index)]

    def _create_entry(self, name, values):
        ''' Render first values as string and place as first code,
            save, and return attr.
        '''
        attr = _PaletteEntry(self, name.upper(), ';'.join(values))
        setattr(self, name, attr)  # now cached
        return attr

    def clear(self):
        ''' Cleanse the palette to free memory.
            Useful for truecolor, perhaps.
        '''
        self.__dict__.clear()


class _PaletteEntry:
    ''' Palette Entry Attribute

        Enables:

        - Rendering to an escape sequence string.
        - Addition of attributes, to create a combined, single sequence.
        - Allows entry attributes to be called, for use as a text wrapper.
        - Use as a Context Manager via the "with" statement.

        Arguments:
            parent  - Parent palette
            name    - Display name, used in demos.
            code    - Associated ANSI code number.
            out     - Stream to print to, when using a context manager.
    '''
    def __init__(self, parent, name, code):
        self.parent = parent
        self.default = (parent.default if hasattr(parent, 'default')
                                       else parent.end)  # style
        self.name = name
        self._codes = [str(code)]           # the initial code
        self._out = sys.stdout              # for redirection

    def __add__(self, other):
        ''' Add: self + other '''
        if isinstance(other, str):
            return str(self) + other

        elif isinstance(other, _PaletteEntry):
            # Make a copy, so codes don't pile up after each addition
            # Render initial values once as string and place as first code:
            newcodes = self._codes + other._codes
            #~ log.debug('codes for new instance: %r', newcodes)  # noisy
            attr = _PaletteEntry(self.parent, self.name,
                                 ';'.join(newcodes))
            same_category = self.parent is other.parent
            #~ log.debug('palette entries match: %s', same_category)  # noisy

            if not same_category:  # different, use end instead of default
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
        log.debug(repr(str(self)))
        print(self, file=self._out, end='')

    def __exit__(self, type, value, traceback):
        print(self.default, file=self._out, end='')

    def __call__(self, text, *styles):
        ''' Formats text.  Not appropriate for huge input strings.

            Tip from Pygments:
                Color sequences are terminated at newlines,
                so that paging the output works correctly.
        '''
        # if the category of styles is different,
        # copy uses fx.end instead of palette.default, see addition:
        for attr in styles:
            self += attr

        pos = text.find('\n', 0, MAX_NL_SEARCH)  # if '\n' in text, w/limit
        if pos != -1:  # found
            lines = text.splitlines()
            for i, line in enumerate(lines):
                lines[i] = f'{self}{line}{self.default}'  # add styles, see tip
            result = '\n'.join(lines)
        else:
            result = f'{self}{text}{self.default}'
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
        self._out = outfile


def _load_x11_color_map(filename=X11_RGB_FILE):
    ''' Load and parse X11's rgb.txt

        Loads:
            _x11_color_map: { name_lower: ('R', 'G', 'B') }
    '''
    try:
        with open(filename) as infile:
            for line in infile:
                if line.startswith('!') or line.isspace():
                    continue

                tokens = line.rstrip().split(maxsplit=3)
                key = tokens[3]
                if ' ' in key:  # skip names with spaces to match webcolors
                    continue

                _x11_color_map[key.lower()] = tuple(tokens[:3])
    except IOError as err:
        log.debug('error: X11 palette not found. %s', err)
