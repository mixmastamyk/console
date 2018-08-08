'''
    console - An easy to use ANSI escape sequence library.
    © 2018, Mike Miller - Released under the LGPL, version 3+.

    A class to mimic ANSI Style container classes so they do not print when the
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
    def __init__(self):
        self.empty = _EmptyAttribute()

    def __getattr__(self, name):
        attr = self.empty
        setattr(self, name, attr)
        return attr


dummy = _DummyCollection()
empty = _EmptyAttribute()
