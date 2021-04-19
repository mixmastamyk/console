'''
    .. © 2018-2020, Mike Miller - Released under the LGPL, version 3+.

    Project metadata is specified here.

    This module *should not* import anything from the project or third-party
    modules, to avoid dependencies in setup.py or circular import issues.
'''
from os.path import join as _join
from time import localtime as _localtime
from types import SimpleNamespace as _Namespace


pkgname         = 'console'
full_name       = 'Console'  # rendered for Makefile
__version__     = version = '0.9907'
__author__      = authors = ', '.join([
                                'Mike Miller',
                                #~ 'and contributors',
                            ])
copyright       = '© 2018-%s' % _localtime().tm_year
description     = ('Comprehensive, composable utility library for ANSI terminals.'
                   ' Better, stronger, faster.  Tch-tch-tch-tch…')
email           = 'mixmastamyk@github.com'
license         = 'LGPL 3',
keywords        = ('ansi terminal emulator console color detection '
                   'escape sequence cursor style screen shell xterm')

# online repo information
repo_account    = 'mixmastamyk'
repo_name       = pkgname
repo_provider   = 'github.com'
doc_url         = 'https://mixmastamyk.bitbucket.io/console/'
repo_url        = 'https://%s/%s/%s' % (repo_provider, repo_account, repo_name)
project_urls    = {'Repository': repo_url, 'Issues': _join(repo_url, 'issues'),
                    'Documentation': doc_url}
home_url = repo_url

trove_classifiers = [
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
    'Programming Language :: Python :: 3.8',
    'Topic :: Software Development :: Libraries',
    'Topic :: Terminals',
]

defaults = _Namespace(
    CURSOR_POS_FALLBACK = (0, 0),
    MAX_CLIPBOARD_SIZE = 65536,  # 64k by default
    MAX_NL_SEARCH = 4096,
    MAX_URL_LEN = 2083,
    MAX_VAL_LEN = 250,
    READ_TIMEOUT = .200,  # select read timeout in float seconds
    TERM_SIZE_FALLBACK = (80, 24),
)
