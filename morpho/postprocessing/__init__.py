"""Perform preprocessing routines designed to run before Stan

Modules:
  - general_data_reducer: Transform any spectrum into
        a histogram of binned data points
  - stan_utility: Perform Stan diagnostic tests
  - data_reducer: Transform a spectrum into a histogram
        of binned data points, for frequency, KE, or time
        spectra. (Soon deprecated by general_data_reducer).
"""

from __future__ import absolute_import

from .data_reducer import *
from .general_data_reducer import *
from .stan_utility import *
