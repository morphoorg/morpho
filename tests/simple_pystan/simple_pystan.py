from morpho.processors.sampling import PyStanSamplingProcessor
from morpho.processors.plots import TimeSeries, APosterioriDistribution

pystan_config = {
    "model_code": "model.stan",
    "input_data": {
        "slope": 1,
        "intercept":-2,
        "xmin":1,
        "xmax":10,
        "sigma": 1.6
    },
    "iterations": 100,
    "interestParams": ['x','y','residual'],

}
aposteriori_config = {
    "n_bins_x": 100,
    "n_bins_y": 100,
    "data": ["y","x",'residual',"lp_prob"],
    "title": "aposteriori_distribution"
}
timeSeries_config = {
    "data": ["x","y"],
    "height": 800,
    "title": "timeseries"
}

pystanProcessor = PyStanSamplingProcessor("pystanProcessor")
aposterioriPlotter = APosterioriDistribution("posterioriDistrib")
timeSeriesPlotter = TimeSeries("timeSeries")

pystanProcessor.Configure(pystan_config)
aposterioriPlotter.Configure(aposteriori_config)
timeSeriesPlotter.Configure(timeSeries_config)
 
result =pystanProcessor.Run()
aposterioriPlotter.data = result
timeSeriesPlotter.data = result
aposterioriPlotter.Run()
timeSeriesPlotter.Run()

