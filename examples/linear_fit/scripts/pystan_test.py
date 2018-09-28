# Basic linear fit example
# This config file can be used to generate and analyze data following an
# linear function. Control plots are then generated.
# Note that each processor are created, configured, run and connected manually
# Author: M. Guigue

from morpho.processors.sampling import PyStanSamplingProcessor
from morpho.processors.plots import TimeSeries, APosterioriDistribution
from morpho.processors.IO import IORProcessor

generator_config = {
    "model_code": "linear_fit/models/model_linear_generator.stan",
    "input_data": {
        "slope": 1,
        "intercept": -2,
        "xmin": 1,
        "xmax": 10,
        "sigma": 1.6
    },
    "iter": 530,
    "warmup": 500,
    "interestParams": ['x', 'y', 'residual'],
}
writer_config = {
    "action": "write",
    "filename": "linear_fit/data/data.r",
    "variables": ["x", "y", 'residual']
}
reader_config = {
    "action": "read",
    "filename": "linear_fit/data/data.r",
    "variables": ["x", "y"]
}
analyzer_config = {
    "model_code": "linear_fit/models/model_linear_fit.stan",
    "iter": 2500,
    "warmup": 500,
    "interestParams": ['slope', 'intercept', 'sigma'],
}
aposteriori_config = {
    "n_bins_x": 100,
    "n_bins_y": 100,
    "variables": ['slope', 'intercept', 'sigma', "lp_prob"],
    "title": "aposteriori_distribution",
    "output_path": "linear_fit/plots"
}
timeSeries_config = {
    "variables": ['slope', 'intercept', 'sigma'],
    "height": 1200,
    "title": "timeseries",
    "output_path": "linear_fit/plots"
}

# Definition of the processors
generationProcessor = PyStanSamplingProcessor("generator")
writerProcessor = IORProcessor("writer")
readerProcessor = IORProcessor("reader")
analysisProcessor = PyStanSamplingProcessor("analyzer")
aposterioriPlotter = APosterioriDistribution("posterioriDistrib")
timeSeriesPlotter = TimeSeries("timeSeries")

# Configuration step
generationProcessor.Configure(generator_config)
writerProcessor.Configure(writer_config)
readerProcessor.Configure(reader_config)
analysisProcessor.Configure(analyzer_config)
aposterioriPlotter.Configure(aposteriori_config)
timeSeriesPlotter.Configure(timeSeries_config)

# Run step
# Generate datapoints
generationProcessor.Run()
writerProcessor.data = generationProcessor.results
# Save data points
writerProcessor.Run()
# Read data points
readerProcessor.Run()
analysisProcessor.data = readerProcessor.data
analysisProcessor.data = {'N': len(analysisProcessor.data['x'])}
# Run analysis on data points
analysisProcessor.Run()
results = analysisProcessor.results
aposterioriPlotter.data = results
timeSeriesPlotter.data = results
# Plot analysis results
aposterioriPlotter.Run()
timeSeriesPlotter.Run()
