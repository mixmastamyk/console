'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    A class to mimic style container classes so they do not print when the
    terminal doesn't support it.
'''


class _EmptyAttribute(str):
    ''' A passive, empty string.  https://youtu.be/sFacWGBJ_cs '''
    name = ''

    def __add__(self, other):
        return self

    def __bool__(self):
        return False

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def __call__(self, *args, **kwargs):
        return ''

    def __str__(self):
        return ''


class _DummyCollection:
    '''  Returns empty strings as attributes. '''
    def __init__(self, empty):
        self.empty = empty

    def __getattr__(self, name):
        ''' Called only when an attribute is missing. '''
        attr = self.empty
        setattr(self, name, attr)   # ready next time
        return attr


empty = _EmptyAttribute()           # TODO: this doesn't show in Sphinx
dummy = _DummyCollection(empty)
