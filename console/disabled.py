'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    Singletons that mimic the style/palette/entry interface but do not print
    ANSI control sequences, i.e.: for use when a terminal doesn't support them.
'''


class _EmptyAttribute(str):
    ''' A passive, empty string.  https://youtu.be/sFacWGBJ_cs '''
    name = ''

    def __add__(self, other):
        return self

    def __bool__(self):
        return False

    def __call__(self, *args, **kwargs):
        if args:
            return args[0]
        else:
            return ''

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def __str__(self):
        return ''


class _EmptyBin:
    '''  Collection that returns empties as attributes. '''
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


empty = _EmptyAttribute()
empty_bin = _EmptyBin(empty)
