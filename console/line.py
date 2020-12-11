'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018-2020, Mike Miller - Released under the LGPL, version 3+.

    Prints fancy lines, similar to HTML header rules, for use in scripts.
'''
import sys, os

from console import fg, fx
from console.detection import get_size
from console.meta import pkgname, __version__


_FALLBACK_SIZE = (80, 20)


def make_line(string='─', width=0, color=None, center=None):
    ''' Build a header-rule style line, using Unicode characters.

        New lines are handled by the caller.
        If the default width of the terminal is used,
        no newline is necessary.
    '''
    auto_width = None
    columns = get_size(_FALLBACK_SIZE).columns

    if width == 0:
        auto_width = True
        width = columns

    line = string * width
    orig_line_len = len(line)

    if color:
        line = getattr(fg, color)(line)
    else:
        line = fx.dim(line)

    if center:
        if auto_width:  # manual width not set
            raise RuntimeError('center parameter must be given with width.')
        else:
            num_spaces = (columns - width) // 2  # floor
            orig_line_len = num_spaces + orig_line_len + num_spaces
            spacing = ' ' * num_spaces
            line = spacing + line + spacing
            if columns > orig_line_len:
                line += ' '

    return line



if __name__ == '__main__':

    def setup():
        ''' Parse command line, validate, initialize logging, etc. '''
        from argparse import ArgumentParser, RawTextHelpFormatter, SUPPRESS
        parser = ArgumentParser(description=__doc__,
                                argument_default=SUPPRESS,
                                formatter_class=RawTextHelpFormatter)

        parser.add_argument('--center', action='store_true',
                            help='Centers when --width was set manually.')
        parser.add_argument('--string', '-s',  metavar='STR',
                            help='Select the character or string to use, unicode ok.')
        parser.add_argument('--color', '-c', metavar='CLR',
                            help='Select a foreground color to draw with,\n'
                            ' defaults to dim.  See docs for names, formats.')
        parser.add_argument('--width', '-w', type=int,
                            metavar='N', help='Select width, auto.')
        parser.add_argument('--version', action='version',
                            version=pkgname + ' ' + __version__)

        # parse and validate
        try:
            args = parser.parse_args()
            if args.center and 'width' not in args:
                parser.error('--center must be given with --width.')

        except SystemExit:
            sys.exit(os.EX_USAGE)

        return args


    def main(args):

        status = os.EX_OK
        try:
            args = vars(args)
            end = '\n' if args.get('width') else ''
            print(make_line(**args), end=end)

        except Exception as err:
            status = os.EX_SOFTWARE
            print(err)

        return status


    sys.exit(main(setup()))
