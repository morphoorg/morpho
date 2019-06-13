# Basic array generator
# This config file can be used to generate list of parameters that have a gaussian
# distribution with means and widths given by the config file.
# Note that each processor are created, configured, run and connected manually
# Author: M. Guigue

from morpho.processors.sampling import PyStanSamplingProcessor
from morpho.processors.plots import TimeSeries, APosterioriDistribution
from morpho.processors.IO import IORProcessor

generator_config = {
    "model_code": "models/gaussian_gen.stan",
    "input_data": {
        "means": [1, 3, 9],
        "widths": [0.5, 1, 0.5]
    },
    "iter": 3000,
    "warmup": 500,
    "interestParams": ['x'],
    "no_diagnostics": True,
    "diagnostics_folder": "plots/generator_diagnostics"
}
writer_config = {
    "action": "write",
    "filename": "data/data.r",
    "variables": ["x[0]", "x[1]"] # here we are saving only the first 2 variables of x
}

# Definition of the processors
generationProcessor = PyStanSamplingProcessor("generator")
writerProcessor = IORProcessor("writer")
# Configuration step
generationProcessor.Configure(generator_config)
writerProcessor.Configure(writer_config)

# Run step
# Generate datapoints
generationProcessor.Run()
writerProcessor.data = generationProcessor.results
# Save data points
writerProcessor.Run()
