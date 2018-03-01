from morpho.processors.sampling import PyStanSamplingProcessor
from morpho.processors.plots import TimeSeries, APosterioriDistribution
from morpho.processors.IO import IORProcessor

generator_config = {
    "model_code": "models/model_linear_generator.stan",
    "input_data": {
        "slope": 1,
        "intercept":-2,
        "xmin":1,
        "xmax":10,
        "sigma": 1.6
    },
    "iter": 530,
    "warmup": 500,
    "interestParams": ['x','y','residual'],
}
writer_config = {
    "action": "write",
    "filename": "data/data.r",
    "variables": ["x","y",'residual']
}
reader_config = {
    "action": "read",
    "filename": "data/data.r",
    "variables": ["x","y"]
}
analyzer_config = {
    "model_code": "models/morpho_linear_fit.stan",
    "iter": 2500,
    "warmup": 500,
    "interestParams": ['slope','intercept','sigma'],
}
aposteriori_config = {
    "n_bins_x": 100,
    "n_bins_y": 100,
    "data": ['slope','intercept','sigma',"lp_prob"],
    "title": "aposteriori_distribution",
    "output_path": "plots"
}
timeSeries_config = {
    "data": ['slope','intercept','sigma'],
    "height": 1200,
    "title": "timeseries",
    "output_path": "plots"
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
 
# Doing things step
writerProcessor.data = generationProcessor.Run()
writerProcessor.Run()
analysisProcessor.data = readerProcessor.Run()
analysisProcessor.data = {'N':len(analysisProcessor.data['x'])}
result = analysisProcessor.Run()

aposterioriPlotter.data = result
timeSeriesPlotter.data = result
aposterioriPlotter.Run()
timeSeriesPlotter.Run()

