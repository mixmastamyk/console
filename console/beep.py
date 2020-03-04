'''
    .. console - Comprehensive utility library for ANSI terminals.
    .. © 2018, Mike Miller - Released under the LGPL, version 3+.

    Cross-platform beep and tone functions.
'''
import logging
import sys
from sys import stdout

from console.detection import os_name
from console.constants import BEL


log = logging.getLogger(__name__)
__version__ = '0.50'
log.info('beepin version: %r', __version__)


try:
    import pyaudio  # Might exist on any OS
    from pyaudio import PyAudio, paUInt8
    import math

    def generate_sine_wave(frequency, duration, volume=0.2, sample_rate=22050):
        ''' Generate a tone at the given frequency.

            Arguments:

                frequency       integer hz
                duration        float seconds
                volume          float 0…1
                sample_rate     integer hz, ie (11_025, 22_050, 44_100, 48_000)

            Limited to unsigned 8-bit samples at a given sample_rate.
            The sample rate should be at least double the frequency.
        '''
        log.debug('generating %shz for %ss', frequency, duration)

        if sample_rate < (frequency * 2):
            log.warn('Warning: sample_rate must be at least double the '
                    f'frequency to accurately represent it:\n    sample_rate '
                    f'{sample_rate} ≯ {frequency*2} (frequency {frequency}*2)')

        num_samples = int(sample_rate * duration)
        rest_frames = num_samples % sample_rate

        pa = PyAudio()
        stream = pa.open(
            format=paUInt8,
            channels=1,  # mono
            rate=sample_rate,
            output=True,
        )
        # make samples
        s = lambda i: volume * math.sin(2 * math.pi * frequency * i / sample_rate)
        samples = (int(s(i) * 0x7F + 0x80) for i in range(num_samples))

        # write several samples at a time, more efficient than it looks
        for buf in zip( *([samples] * sample_rate) ):
            stream.write(bytes(buf))

        # fill remainder of frameset with silence
        stream.write(b'\x80' * rest_frames)

        stream.stop_stream()
        stream.close()
        pa.terminate()

except ImportError:
    pyaudio = None


def beep_windows(**kwargs):
    ''' Simple system beep for Windows. '''
    import winsound

    log.debug('trying winsound.MessageBeep…')
    winsound.MessageBeep()  # the standard windows bell


def beep_macos(posix=False):
    ''' Simple system beep for MacOS. '''
    if posix:
        beep_posix()
    else:
        # Note: makes the terminal/app icon in the taskbar jump.
        log.debug('trying AppKit.NSBeep…')
        from AppKit import NSBeep
        NSBeep()


def beep_posix(**kwargs):
    ''' Simple system beep for POSIX terminals, may be disabled. '''
    log.debug('outputting BEL…')
    stdout.write(BEL)
    stdout.flush()


def beep_tone_windows(frequency_hz, duration_ms, **kwargs):
    ''' Generate a beep tone, for Windows. '''
    import winsound
    log.debug('trying winsound.Beep…')
    winsound.Beep(frequency_hz, duration_ms)  # e.g. (1000, 500)


def beep_tone_macos(frequency_hz, duration_ms, **kwargs):
    ''' Generate a beep tone. '''
    msg = 'Tone generation not yet implemented on darwin.'
    log.warning(msg)
    raise NotImplementedError(msg)


def beep_tone_pyaudio(frequency_hz, duration_ms, volume=0.2, sample_rate=22050,
                      **kwargs):
    ''' Generate a beep tone. '''
    log.debug('trying PyAudio…')
    import pyaudio;  pyaudio  # pyflakes
    generate_sine_wave(
        frequency=frequency_hz,
        duration=duration_ms/1000,  # float seconds
        volume=volume,
        sample_rate=sample_rate,
    )


def beep_play(sound_file, **kwargs):
    ''' Play audio files for beeps, requires boombox to be installed. '''
    from boombox import play

    boombox = play(sound_file, **kwargs)
    return boombox


# ----------------------------------------------------------------------------
# Load a default implementation at beep*()
beep = lambda f, d: log.error('beep impl. not loaded. (%s, %s)', f, d)
beep_tone = lambda f, d : log.error('beep impl. not loaded. (%s, %s)', f, d)


if os_name == 'nt':             # I'm a PC
    beep = beep_windows
    beep_tone = beep_tone_windows

elif sys.platform == 'darwin':  # Think different
    try:
        import AppKit;  AppKit  # pyflakes
        beep = beep_macos
    except ImportError:
        AppKit = None
        beep = beep_posix
    if pyaudio:
        beep_tone = beep_tone_pyaudio
    else:
        beep_tone = beep_tone_macos

elif os_name == 'posix':        # Tron leotards
    beep = beep_posix
    if pyaudio:
        beep_tone = beep_tone_pyaudio
    else:
        log.warning('Tone generation not available, try: pip install PyAudio.')


if __name__ == '__main__':

    import time
    import sys

    from console import fg, fx, defx

    if '-d' in sys.argv:
        try:
            import out
            out.configure(level='debug')
        except ImportError:
            logging.basicConfig(level='DEBUG',
                format=('%(levelname)s '
                f'{fx.dim}%(funcName)s:{fg.green}%(lineno)s{fg.default}{defx.dim}'
                ' %(message)s'),
            )

    if os_name == 'nt':
        sound_file = 'c:/Windows/Media/Alarm08.wav'

    elif sys.platform == 'darwin':
        if not AppKit:
            log.warning('Note: pyobjc not installed: pip install pyobjc')
        sound_file = '/System/Library/Sounds/Ping.aiff'

    elif os_name == 'posix':
        sound_file = '/usr/share/sounds/ubuntu/stereo/phone-outgoing-busy.ogg'

    # Try all three
    log.info('beepin version: %r', __version__)
    log.info('System Beep…')
    beep()
    log.debug('sleeping…')
    time.sleep(2)
    print()

    log.info('Generate Tone…')
    beep_tone(frequency_hz=500, duration_ms=1000, volume=.1)
    log.debug('sleeping…')
    time.sleep(2)
    print()

    log.info('Sound File… %r', sound_file)
    boombox = beep_play(
        sound_file=sound_file,
        duration_ms=2_000,
        #~ wait=True,
        wait=False,
    )
    log.debug('cutting short…')
    time.sleep(.5)
    boombox.stop()
    time.sleep(1)
    log.debug('starting again…')
    boombox.play()
    log.debug('sleeping…')
    time.sleep(2)
    print()

    if True and os_name == 'nt':
        log.info('Trying Alias…')
        beep_play(
            #~ sound_file='SystemAsterisk',
            #~ sound_file='SystemExclamation',
            #~ sound_file='SystemExit',
            sound_file='SystemHand',
            #~ sound_file='SystemQuestion',
            is_alias=True,
            duration_ms=2_000,
            wait=True,
            #~ wait=False,
        )
        log.debug('sleeping…')
        time.sleep(1)
        log.debug('done')
