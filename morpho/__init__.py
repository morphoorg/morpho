"""All modules and packages used by morpho

Subpackages:
    preprocessing: Process inputs before passing to stan
    loader: Load data for use by stan
    plot: Create plots from stan outputs
    postprocessing: Process stan outputs before or after plotting
"""

from __future__ import absolute_import

import pkg_resources
__version__ = pkg_resources.require("morpho")[0].version.split('-')[0]
__commit__ = pkg_resources.require("morpho")[0].version.split('-')[-1]

# from . import plot
# from . import preprocessing
# from . import postprocessing
# from . import loader

# morpho2
from . import utilities
from . import processors


