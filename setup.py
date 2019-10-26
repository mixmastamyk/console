import sys
from os.path import dirname, join
from setuptools import setup


assert sys.version_info >= (3, 4, 0), "This package requires Python 3.4+"
# avoid starting console detection:
import imp
meta = imp.load_source('meta', 'console/meta.py')


if sys.version_info.major < 3:
    raise NotImplementedError('Sorry, only Python 3 and above is supported.')

# https://www.python.org/dev/peps/pep-0508/#environment-markers
install_requires = (
    'ezenv',
    'future_fstrings;     python_version < "3.6" ',
    'typing;              python_version < "3.5" ',  # seems future-fs related.
    'colorama;            os_name == "nt" and platform_version < "10.0.10586" ',
    'win_unicode_console; os_name == "nt" and python_version < "3.6" ',
)
tests_require = ('pyflakes', 'pytest', 'readme_renderer'),
extras_require = dict(
    webcolors=('webcolors',),
)

def slurp(filename):
    try:
        with open(join(dirname(__file__), filename), encoding='utf8') as infile:
            return infile.read()
    except FileNotFoundError:
        pass  # needed at upload time, not install time


setup(
    name                = meta.pkgname,
    description         = meta.description,
    author_email        = meta.email,
    author              = meta.authors,
    keywords            = meta.keywords,
    license             = 'LGPL 3',
    long_description    = slurp('readme.rst'),
    packages            = (meta.pkgname,),
    url                 = meta.repo_url,
    version             = meta.version,

    extras_require      = extras_require,
    install_requires    = install_requires,
    python_requires     = '>=3.4',  # untested below that
    setup_requires      = install_requires,
    tests_require       = tests_require,
    classifiers         = meta.trove_classifiers,
)
