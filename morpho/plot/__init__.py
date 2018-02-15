"""Plotting routines for use after Stan

Modules:
  - contours: Create a matrix of contour plots from a stanfit object
  - histo: Plot 1D and 2D histograms
  - neutrino_params: Example to plot quantities for a neutrino mass analysis
  - plotting_routines: Private functions used in other plotting modules
  - spectra: Plot spectra related to a neutrino mass analysis
  - timeseries: Save multiple plots in a root file
"""

from __future__ import absolute_import

from .plotting_routines import *

from .contours import *
from .histo import *
from .neutrino_params import *
from .spectra import *
from .timeseries import *
