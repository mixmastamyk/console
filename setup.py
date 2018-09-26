#!/usr/bin/env python3
import sys
from os.path import dirname, join
from setuptools import setup


# additional metadata, requirements
keywords = ('ansi color detection escape terminal console sequence cursor '
            'style screen shell')
install_requires = ['ezenv',]
tests_require = ('pyflakes', 'pytest', 'readme_renderer'),
extras_require = dict(
    webcolors=('webcolors',),
    colorama=('colorama',),
)


def slurp(filename):
    try:
        with open(join(dirname(__file__), filename), encoding='utf8') as infile:
            return infile.read()
    except FileNotFoundError:
        pass  # needed at upload time, not install time


if sys.version_info.major < 3:
    raise NotImplementedError('Sorry, only Python 3 and above is supported.')

if sys.version_info.minor < 6:
    install_requires.append('future_fstrings')
    install_requires.append('win_unicode_console')


setup(
    name                = 'console',
    description         = 'Comprehensive utility library for ANSI terminals. '
                          'Better, stronger, faster.',
    author_email        = 'mixmastamyk@github.com',
    author              = 'Mike Miller',
    keywords            = keywords,
    license             = 'LGPL 3',
    long_description    = slurp('readme.rst'),
    packages            = ('console',),
    url                 = 'https://github.com/mixmastamyk/console',
    version             = '0.87a2',

    extras_require      = extras_require,
    install_requires    = install_requires,
    python_requires     = '>=3.2',
    setup_requires      = install_requires,
    tests_require       = tests_require,

    classifiers         = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Terminals',
    ],
)
