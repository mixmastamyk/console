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
keywords = 'ansi terminal escape sequence color cursor style screen detection'
tests_require = ('pytest'),


def slurp(filename):
    with open(join(dirname(__file__), filename)) as infile:
        return infile.read()


setup(
    name                = 'console',
    description         = 'Comprehensive escape sequence utility library for terminals.',

    author_email        = 'mixmastamyk@github.com',
    author              = 'Mike Miller',
    extras_require      = extras_require,
    install_requires    = install_requires,
    keywords            = keywords,
    license             = 'LGPL 3',
    long_description    = slurp('readme.rst'),
    packages            = ('console',),
    tests_require       = tests_require,
    url                 = 'https://github.com/mixmastamyk/console',
    version             = __version__,

    classifiers     = [
        'Development Status :: 3 - Alpha',
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


#~ extras_require = dict(pygments='pygments')
#~ python_requires Python 3.6.0
