"""All modules and packages used by morpho

Subpackages:
  - preprocessing: Process inputs before passing to stan
  - loader: Load data for use by stan
  - plot: Create plots from stan outputs
  - postprocessing: Process stan outputs before or after plotting
"""

from __future__ import absolute_import

import pkg_resources
__version__ = pkg_resources.require("morpho")[0].version.split('-')[0]
__commit__ = pkg_resources.require("morpho")[0].version.split('-')[-1]

# from . import processors
# from . import utilities

__all__ = []
import pkgutil
import inspect

for loader, name, is_pkg in pkgutil.walk_packages(__path__):
    module = loader.find_module(name).load_module(name)
    for name, value in inspect.getmembers(module):
        if name.startswith("__"):
          continue
        globals()[name] = value
        __all__.append(name)
