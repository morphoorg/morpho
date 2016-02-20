'''
'''

from __future__ import absolute_import

import pkg_resources
__version__ = pkg_resources.require("morpho")[0].version.split('-')[0]
__commit__ = pkg_resources.require("morpho")[0].version.split('-')[-1]

from . import implementations
from . import status_log_handlers
from . import subcommands
