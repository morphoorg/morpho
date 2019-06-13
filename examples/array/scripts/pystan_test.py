# Basic array generator
# This config file can be used to generate list of parameters that have a gaussian
# distribution with means and widths given by the config file.
# Note that each processor are created, configured, run and connected manually
# Author: M. Guigue

from morpho.processors.sampling import PyStanSamplingProcessor
from morpho.processors.plots import TimeSeries, APosterioriDistribution
from morpho.processors.IO import IOROOTProcessor

generator_config = {
    "model_code": "models/gaussian_gen.stan",
    "input_data": {
        "means": [1, 3, 9],
        "widths": [0.5, 1, 0.5]
    },
    "iter": 3000,
    "warmup": 500,
    "interestParams": ['x', 'y'],
    "no_diagnostics": True,
    "diagnostics_folder": "plots/generator_diagnostics"
}
writer_config = {
    "action": "write",
    "tree_name": "test",
    "filename": "myTest.root",
    "variables": [
        {
            "variable": "y",
            "root_alias": "y",
            "type": "float"
        },
        {
            "variable": "x[0]",
            "root_alias": "value0",
            "type": "float"
        },
        {
            "variable": "x[1]",
            "root_alias": "value1",
            "type": "float"
        }
    ]
}

# Definition of the processors
generationProcessor = PyStanSamplingProcessor("generator")
writerProcessor = IOROOTProcessor("writer")
# Configuration step
generationProcessor.Configure(generator_config)
writerProcessor.Configure(writer_config)

# Run step
# Generate datapoints
generationProcessor.Run()
writerProcessor.data = generationProcessor.results
# Save data points
writerProcessor.Run()
