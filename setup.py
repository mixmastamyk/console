#!/usr/bin/env python3
import sys
from os.path import dirname, join
from setuptools import setup


if sys.version_info.major < 3:
    raise NotImplementedError('Sorry, only Python 3 and above is supported.')

# additional metadata, requirements
keywords = ('ansi color detection escape terminal console sequence cursor '
            'style screen shell xterm')

# https://www.python.org/dev/peps/pep-0508/#environment-markers
install_requires = [
    'ezenv',
    'future_fstrings;     python_version < "3.6" ',
    'colorama;            os_name == "nt" and platform_version < "10.0.10586" ',
    'win_unicode_console; os_name == "nt" and python_version < "3.6" ',
]
tests_require = ('pyflakes', 'pytest', 'readme_renderer'),
extras_require = dict(
    webcolors=('webcolors',),
)

# read version as text to avoid machinations at import time:
version = '1.00'
with open('console/__init__.py') as infile:
    for line in infile:
        if line.startswith('__version__'):
            try:
                version = line.split("'")[1]
            except IndexError:
                pass
            break

def slurp(filename):
    try:
        with open(join(dirname(__file__), filename), encoding='utf8') as infile:
            return infile.read()
    except FileNotFoundError:
        pass  # needed at upload time, not install time


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
    version             = version,

    extras_require      = extras_require,
    install_requires    = install_requires,
    python_requires     = '>=3.4',  # untested below that
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
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries',
        'Topic :: Terminals',
    ],
)
