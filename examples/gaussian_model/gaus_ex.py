# Basic gaussian data generator (exercise).
# This script will generate fake data following a gaussian distribution, after you complete it
# Good luck! :D
# Author: M. Guigue
# Date: 11/11/2018

from morpho.processors.plots import Histogram
from morpho.processors.sampling import GaussianSamplingProcessor
from morpho.utilities import morphologging

logger = logger = morphologging.getLogger(__name__)

logger.info("Defining gaussian processor generator and histogram configurations")
gauss_config = {
    "mean": 5,
    "width": 2,
    "iter": 10000
}
histo_config = {
    "variables": "x",
    "n_bins_x": 300,
    "output_path": ".",
    "title": "Gaussian sample",
    "format": "pdf"
}

logger.info("Defining processors")
sampler = ...
myhisto = ...

logger.info("Configuring processors")
...
...

logger.info("Running sampler first")
...
logger.info("Connecting sampler output (results) to histo input (data)")
...
logger.info("Running myhisto")
...

logger.info("Done!")
