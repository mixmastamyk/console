'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2020, Mike Miller - Released under the LGPL, version 3+.

    Convenience command-line interface script for select utility functions
    and methods that don't have common implementations,
    such as tput.
    (Optional arguments may be shortened and are recognized when unique.)
'''
import sys, os
import logging
from importlib import import_module
from inspect import signature

from . import fg, fx
from .meta import __version__


log = logging.getLogger(__name__)
actions = dict(
    # function            module or function
    _print_ascii_chart  = 'console.ascii4',         # hide
    ascii               = ['_print_ascii_chart'],   # alias

    beep                = 'console.beep',
    _init               = 'console.detection',  # hide
    detect              = ['_init'],            # alias
    get_theme           = 'console.detection',

    _detect_unicode_support = 'console.detection',  # hide
    detect_unicode      = ['_detect_unicode_support'],  # alias

    progress            = 'console.progress',

    clear_lines         = 'console.utils',
    flash               = 'console.utils',
    get_clipboard       = 'console.utils',
    #~ len_stripped        = 'console.utils',
    sized               = ['make_sized'],       # alias
    line                = ['make_line'],        # alias
    link                = ['make_hyperlink'],   # alias
    make_sized          = 'console.utils',
    make_hyperlink      = 'console.utils',
    make_line           = 'console.utils',
    measure             = 'console.utils',
    _notify_message     = 'console.utils',
    notify_msg          = ['_notify_message'],
    pause               = 'console.utils',
    set_clipboard       = 'console.utils',
    set_title           = 'console.utils',
    strip_ansi          = 'console.utils',
    wait_key            = 'console.utils',
    view                = 'console.viewers',

    _hrender            = 'console.viewers',    # hide
    echo                = ['_hrender'],         # alias
)
if os.name == 'nt':  # :-/
    from .windows import add_os_sysexits
    add_os_sysexits()


def _add_sub_args(parameters, sub_parser, allow_kwargs, verbose):
    ''' Given function signature parameters, add to parser. '''

    for name, param in parameters.items():

        if name.startswith('_'):  # skip these
            continue

        prefix = '--'  # defaults
        type_ = str
        if param.annotation is not param.empty:  # allow override
            type_ = param.annotation
        elif param.kind.name == 'VAR_KEYWORD':  # **kwargs
            allow_kwargs = True
            continue
        elif param.default is None:
            pass
        elif param.default is param.empty:
            pass
        else:
            type_ = type(param.default)

        # figure params to the sub_parser argument:
        if param.default is param.empty:
            default_text = ''
        else:
            default_text = f', defaults to {param.default!r}'

        sub_args = dict(
            default=param.default,
            help=f'{type_.__name__}{default_text}',
        )
        if type_ is bool:
            if param.default:  # default True, negate boolean flag
                sub_args['action'] = 'store_false'
                sub_args['dest'] = name
                sub_args['help'] = f'{type_.__name__}, negates default'
                name = 'no-' + name
            else:
                sub_args['action'] = 'store_true'
        else:
            if param.default is param.empty:
                prefix = ''
            else:
                sub_args['metavar'] = type_.__name__[0].upper()
            sub_args['type'] = type_

        if verbose:
            log.debug('param: %s', (fg.green + fx.bold)(name))
            log.debug('  default: %r' % param.default)
            log.debug('  annotat: %r', param.annotation)
            log.debug('  kind    %r:', param.kind.name)
            log.debug('  type    %r:', type_)
            log.debug('  sub add_argument: %r', sub_args)

        name = name.replace('_', '-')
        sub_parser.add_argument(prefix + name, **sub_args)

    return allow_kwargs


def _get_action_help(choices):
    ''' Build the action list help string. '''
    from textwrap import fill

    ac_list = [ fg.green(action) for action in choices ]
    return fill('{%s}' % ', '.join(ac_list), width=90)  # wider due to escapes


def _parse_extras(parser, extras):
    ''' Given a list of '--key', 'value' strings, return a dictionary. '''
    new = {}
    keys = []
    for arg in extras:
        if arg.startswith('--'):
            suffix = arg[2:]
            key, _, val = suffix.partition('=')  # --name=value form?
            if val:
                new[key] = val
            else:
                keys.append(suffix)
        elif keys:
            new[keys.pop()] = arg
        else:
            parser.error('no extra positional arguments allowed: %r' % arg)

    return new


def setup():
    ''' Parse command line, validate, initialize logging, etc. '''
    from argparse import ArgumentParser, RawTextHelpFormatter as RawFormatter

    # text styles
    op, n = fx.dim, fx.end  # options, normal
    opv = fx.italic + op  # variable/abstract in italic
    ac = fg.lightgreen  # actions
    acv = fx.italic + ac
    _action = acv('action')

    action_choices = sorted(set(f for f in actions if not f.startswith('_')))
    action_help = _get_action_help(action_choices)

    # build top-level parser
    parser = ArgumentParser(
        add_help=False, description=__doc__, formatter_class=RawFormatter,
        usage=f'%(prog)s {op}-v{n} {op}--version{n} {_action} {opv}options…{n}',
    )
    parser.add_argument(
        'action', nargs='?', choices=action_choices,
        metavar=_action + '  ',  # clear clumsy action help, better fmt-ing:
        help='   one of ' + action_help +
            f'\n(use {_action} {op}-h{n} for specific help)',
    )
    parser.add_argument(
        '-n', action='store_const', dest='newline', default='\n', const='',
        help='do not output the trailing newline',
    )
    parser.add_argument(
        '-v', '--verbose', action='store_const', dest='loglvl',
        default=logging.INFO, const=logging.DEBUG,
        help='print additional information',
    )
    parser.add_argument(
        '--version', action='version', version='%(prog)s ' + __version__
    )
    # parse and validate
    args, extras = parser.parse_known_args()  # don't complain about extras
    verbose = args.loglvl == logging.DEBUG
    newline = args.newline

    # start logging
    logging.basicConfig(
        level=args.loglvl,
        stream=sys.stdout,
        format='  %(levelname)-8.8s %(message)s',
    )
    logging.captureWarnings(True)
    log.debug('console cli, version: %s', __version__)
    log.debug('args: %s', args)
    if extras: log.debug('extr: %s', extras)

    if args.action:
        # Build a sub parser with a new parser, so we don't have to build a
        # sub parser for every conceivable command at start up only to
        # pick one, also simplifies a few things:
        sub_parser = ArgumentParser(
            formatter_class=RawFormatter,
            usage=f'%(prog)s {ac(args.action)} {opv}args…{n} {opv}options…{n}',
        )
        allow_kwargs = False
        # find module and function
        funcname = args.action
        value = actions[funcname]
        if type(value) is list:  # for aliases, value is function name
            funcname = value[0]
            modname = actions[funcname]  # try again
            funcname = funcname.lstrip('_')  # in case it was hidden
        else:
            modname = value

        # load, store, and inspect signature
        mod = import_module(modname)
        funk = getattr(mod, funcname)
        if '-h' in sys.argv:  # avoid extra work when subparser not ready
            from textwrap import dedent, indent
            sub_parser.description = indent(
                dedent('       ' + funk.__doc__), '    '
            )
        else:
            sub_parser.set_defaults(_funk=funk)

        # configure sub parser
        allow_kwargs = _add_sub_args(
            signature(funk).parameters, sub_parser, allow_kwargs, verbose
        )
        # finally, parse and validate subcmd args
        if allow_kwargs:
            args, extras = sub_parser.parse_known_args(extras)
            kwargs = _parse_extras(sub_parser, extras)
        else:
            args, kwargs = sub_parser.parse_args(extras), {}
        args._newline = newline  # copy from original

    else:  # no action, quit
        parser.print_help()
        sys.exit(os.EX_USAGE)

    return args, kwargs


def main(args, kwargs):
    ''' Tear the roof off the sucker… '''
    status = os.EX_OK
    print_err = lambda err: print(f'{err.__class__.__name__}: {err}')

    try:  # Ow, we want the funk…
        options = vars(args)
        funk = options.pop('_funk', None)  # Give up the funk
        nl = options.pop('_newline', None)

        if funk:
            log.debug('running: %s %s', funk, options)
            log.debug('-' * 60)
            result = funk(**options, **kwargs)
            if result:
                print(result, end=nl)
            log.debug('result was: %r', result)

    except FileNotFoundError as err:
        print_err(err)
        status = os.EX_NOINPUT

    except IOError as err:
        print_err(err)
        status = os.EX_IOERR

    except Exception as err:
        if log.isEnabledFor(logging.DEBUG):
            log.exception('Unexpected error occurred:')
        else:
            print_err(err)
        status = os.EX_SOFTWARE

    # You've got a real type of thing going down, gettin' down
    # There's a whole lot of rhythm going round…
    log.debug('done, with status: %r', status)
    return status


def setuptools_entry_point():
    ''' This is the new way to get an .exe on Windows.  :-/ '''

    return main(*setup())


if __name__ == '__main__':

    sys.exit(main(*setup()))
