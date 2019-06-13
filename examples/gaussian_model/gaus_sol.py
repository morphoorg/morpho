# Basic gaussian data generator (solution)
# This script will generate fake data following a gaussian distribution.
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
sampler = GaussianSamplingProcessor("sampler")
myhisto = Histogram("histo")

logger.info("Configuring processors")
sampler.Configure(gauss_config)
myhisto.Configure(histo_config)

logger.info("Running sampler first")
sampler.Run()
logger.info("Connecting sampler output (results) to histo input (data)")
myhisto.data = sampler.results
logger.info("Running myhisto")
myhisto.Run()

logger.info("Done!")
