'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018-2025, Mike Miller - Released under the LGPL, version 3+.

    Cross-platform beep functions.
    See BoomBox for audio-file playback and tone-generation for sound effects.
'''
import logging
import sys
from sys import stdout

import env

from . import using_terminfo
from console.detection import os_name
from console.constants import BEL
from console.meta import version


log = logging.getLogger(__name__)


def _check_environment():
    ''' Warn if we're in an audio-poor environment. '''
    if env.TERM in ('linux', 'fbterm'):
        log.debug('Warning: console beep may require `sudo modprobe pcspkr` '
                  'or an audio playback module such as BoomBox.')


def beep_curses():
    ''' Curses beep. '''
    _check_environment()
    log.debug('trying curses.beep…')
    curses.beep()


def beep_macos(wait_secs=.5):
    ''' Simple audio-system beep for MacOS.

        If the program runs too quickly it will get killed before the sound
        is played.  A small sleep, say .5 seconds afterward may be necessary.
    '''
    log.debug('trying AppKit.NSBeep…')
    from AppKit import NSBeep

    NSBeep()
    if wait_secs:
        from time import sleep
        sleep(wait_secs)


def beep_posix():
    ''' Simple system beep for POSIX terminals, may be disabled. '''
    _check_environment()
    log.debug('outputting BEL…')
    stdout.write(BEL)
    stdout.flush()


def beep_windows():
    ''' Simple audio-system beep for Windows. '''
    import winsound

    log.debug('trying winsound.MessageBeep…')
    winsound.MessageBeep()  # the standard windows bell


# ----------------------------------------------------------------------------
beep = lambda *args: log.error('beep impl. not loaded. (%s)', args)


# Load a default implementation at beep()
if os_name == 'nt':                     # I'm a PC
    beep = beep_windows

else:
    if using_terminfo:
        import curses
        curses.initscr()
        beep = beep_curses
    else:
        if sys.platform == 'darwin':    # Think diffr'nt
            #~ try:
                #~ import AppKit
                #~ beep = beep_macos
            #~ except ImportError:
                 #~ AppKit = None
            # default to posix, less troublesome:
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
