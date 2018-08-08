#!/usr/bin/env python

# tests require pytest

from os.path import dirname, join
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

from console.constants import __version__

keywords = 'ansi terminal color cursor style pycolor escape sequence blessings'
tests_require = ('pytest'),
install_requires = ('ezenv',)


def read(fname):
    with open(join(dirname(__file__), fname)) as f:
        return f.read()


setup(
    name                = 'console',

    author_email        = 'mixmastamyk@github.com',
    author              = 'Mike Miller',
    description         = 'A more comprehensive, easy to use ANSI library.',
    keywords            = keywords,
    license             = 'LGPL 3',
    long_description    = read('readme.rst'),
    packages            = ('console',),
    install_requires    = install_requires,
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
