'''
    Project metadata is specified here.

    This module *should not* import anything from the project or third-party
    modules, to avoid dependencies in setup.py or circular import issues.
'''
from time import localtime as _localtime


pkgname         = 'console'
__version__     = version = '0.98'
__author__      = authors = ', '.join([
                                'Mike Miller',
                                #~ 'and contributors',
                            ])
copyright       = '© 2018-%s' % _localtime().tm_year
description     = ('Comprehensive, composable utility library for ANSI terminals.'
                   ' Better, stronger, faster.  Tch-tch-tch-tch…')
email           = 'mixmastamyk@github.com'
license         = 'LGPL 3',
keywords        = ('ansi color detection escape terminal console sequence '
                   'cursor style screen shell xterm')

# online repo information
repo_account    = 'mixmastamyk'
repo_name       = pkgname
repo_provider   = 'github.com'
repo_url        = 'https://%s/%s/%s' % (repo_provider, repo_account, repo_name)


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
    'Topic :: Software Development :: Libraries',
    'Topic :: Terminals',
]

class defaults:
    CURSOR_POS_FALLBACK = (0, 0)
    MAX_NL_SEARCH = 4096
    READ_TIMEOUT = .200  # select read timeout in float seconds
    TERM_SIZE_FALLBACK = (80, 24)
