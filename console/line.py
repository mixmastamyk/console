'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018-2020, Mike Miller - Released under the LGPL, version 3+.

    Prints fancy lines, similar to HTML header rules, for use in scripts.
'''
import sys, os

from console import fg, fx
from console.detection import get_size
from console.meta import pkgname, __version__

_fallback_width = (80, 20)


def setup():
    ''' Parse command line, validate, initialize logging, etc. '''
    from argparse import ArgumentParser, RawTextHelpFormatter
    parser = ArgumentParser(description=__doc__,
                            formatter_class=RawTextHelpFormatter)

    parser.add_argument('--center', action='store_true',
                        help='Centers when --width was set manually.')
    parser.add_argument('--character', '-c',  metavar='C', default='─',
                        help='Select the character to draw, unicode happy.')
    parser.add_argument('--style', '-s', metavar='STR',
                        help='Select a foreground color to draw with,\n'
                        ' defaults to dim.  See docs for indexed or direct names.')
    parser.add_argument('--width', '-w', type=int, default=0, metavar='N',
                        help='Select width, auto.')

    parser.add_argument('--version', action='version',
                        version=pkgname + '/%(prog)s ' + __version__)

    # parse and validate
    try:
        args = parser.parse_args()
    except SystemExit:
        sys.exit(os.EX_USAGE)

    return args


def main(args):

    status = os.EX_OK
    end = ''
    try:
        terminal_width = get_size(_fallback_width)[0]

        if args.width == 0:
            args.width = terminal_width
        else:
            args._add_newline = True

        line = args.character * args.width

        if args.style:
            line = getattr(fg, args.style)(line)
        else:
            line = fx.dim(line)

        if hasattr(args, '_add_newline'):
            end = '\n'
            if args.center:
                spaces = (terminal_width - args.width) // 2
                line = (' ' * spaces)  + line

        print(line, end=end)

    except Exception as err:
        status = os.EX_SOFTWARE
        print(err)

    return status


if __name__ == '__main__':

    sys.exit(main(setup()))

