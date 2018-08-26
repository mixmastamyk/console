#!/usr/bin/env python3

from os.path import dirname, join
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from console.constants import __version__


# additional metadata
extras_require = dict(
    webcolors=('webcolors',),
    colorama=('colorama',),
)
install_requires = ('ezenv',)
keywords = ('ansi color detection escape terminal console sequence cursor '
            'style screen shell')
tests_require = ('pyflakes', 'pytest', 'readme_renderer'),


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
    extras_require      = extras_require,
    install_requires    = install_requires,
    keywords            = keywords,
    license             = 'LGPL 3',
    long_description    = slurp('readme.rst'),
    packages            = ('console',),
    python_requires     = '>=3.6',
    tests_require       = tests_require,
    url                 = 'https://github.com/mixmastamyk/console',
    version             = __version__,

    classifiers         = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
        'Topic :: Terminals',
    ],
)
