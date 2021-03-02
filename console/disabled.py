'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    Singletons that mimic the style/palette/entry interface but do not print
    ANSI control sequences, i.e.: for use when a terminal doesn't support them.
'''


class _EmptyAttribute(str):
    ''' A passive, empty, and "falsey" string.

        https://youtu.be/sFacWGBJ_cs
    '''
    name = ''

    def __add__(self, other):  # empty, so return other
        return other

    def __radd__(self, other):
        return other

    def __bool__(self):
        return False

    def __call__(self, text, *args, **kwargs):
        return text

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def __str__(self):
        return ''


class _EmptyScreenAttribute(_EmptyAttribute):
    ''' A passive, empty, and "falsey" string.

        Screen methods need to return blank strings, even when passed integer
        arguments.
    '''
    def __call__(self, *args, **kwargs):
        return ''


class _EmptyBin:
    ''' Collection that returns EmptyAttributes on any attribute access. '''
    def __init__(self, an_empty):
        self.an_empty = an_empty

    def __getattr__(self, name):
        ''' Called only when an attribute is missing. '''
        attr = self.an_empty
        setattr(self, name, attr)   # ready next time
        return attr

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def __repr__(self):
        return f'{self.__class__.__name__}()'


# It's Automatic:  https://youtu.be/y5ybok6ZGXk
empty = _EmptyAttribute()
empty_bin = _EmptyBin(empty)
empty_scr_bin = _EmptyBin(_EmptyScreenAttribute())
