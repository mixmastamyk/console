'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018-2020, Mike Miller - Released under the LGPL, version 3+.

    Cross-platform beep functions.
    See BoomBox for audio-file playback and tone-generation for sound effects.
'''
import logging
import sys
from sys import stdout


from console.detection import os_name
from console.constants import BEL
from console.meta import version


log = logging.getLogger(__name__)


def beep_windows(**kwargs):
    ''' Simple system beep for Windows. '''
    import winsound

    log.debug('trying winsound.MessageBeep…')
    winsound.MessageBeep()  # the standard windows bell


def beep_macos(**kwargs):
    ''' Simple system beep for MacOS. '''
    # Note: makes the terminal/app icon in the taskbar jump.
    log.debug('trying AppKit.NSBeep…')
    from AppKit import NSBeep
    NSBeep()


def beep_posix(**kwargs):
    ''' Simple system beep for POSIX terminals, may be disabled. '''
    import env
    if env.TERM in ('linux', 'fbterm'):
        log.debug('Warning: console beep may require `sudo modprobe pcspkr` '
                  'or an audio playback module such as BoomBox.')
    log.debug('outputting BEL…')
    stdout.write(BEL)
    stdout.flush()


# ----------------------------------------------------------------------------
beep = lambda *args: log.error('beep impl. not loaded. (%s)', args)


# Load a default implementation at beep()
if os_name == 'nt':             # I'm a PC
    beep = beep_windows

elif sys.platform == 'darwin':  # Think different
    try:
        import AppKit
        beep = beep_macos
    except ImportError:
        AppKit = None
        beep = beep_posix

elif os_name == 'posix':        # Tron leotards
    beep = beep_posix


if __name__ == '__main__':

    import sys
    from time import sleep

    from console import fg, fx, defx

    if '-d' in sys.argv:
        try:
            import out
            out.configure(level='debug')
        except ImportError:
            logging.basicConfig(level='DEBUG',
                format=('%(levelname)-7.7s '
                f'{fx.dim}%(funcName)s:{fg.green}%(lineno)s{fg.default}{defx.dim}'
                ' %(message)s'),
            )

    log.debug('console version: %r', version)
    beep()
    sleep(.5)
