'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018-2020, Mike Miller - Released under the LGPL, version 3+.

    Prints a fancy line (similar to HTML header rules) for use in scripts.

    DEPRECATED - going to move this and others to a dedicated command.
'''
import sys, os

from .meta import pkgname, __version__
from .utils import make_line


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
            if 'center' in args and 'width' not in args:
                parser.error('--center must be given with --width.')

        except SystemExit:
            sys.exit(os.EX_USAGE)

        return args


    def main(args):

        status = os.EX_OK
        try:
            args = vars(args)
            #~ end = '\n' if args.get('width') else ''
            end = ''
            print(make_line(**args), end=end)

        except Exception as err:
            status = os.EX_SOFTWARE
            print(err)

        return status


    sys.exit(main(setup()))
