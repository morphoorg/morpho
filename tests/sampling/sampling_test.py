'''
This scripts aims at testing sampling processors by generating data and analyzing them.
Author: M. Guigue
Date: Feb 27 2018
'''

import unittest

from morpho.utilities import morphologging
logger = morphologging.getLogger(__name__)


class SamplingTests(unittest.TestCase):

    def test_PyStan(self):
        logger.info("PyStanSampling test")
        from morpho.processors.sampling import PyStanSamplingProcessor

        pystan_config = {
            "model_code": "model.stan",
            "input_data": {
                "slope": 1,
                "intercept": -2,
                "xmin": 1,
                "xmax": 10,
                "sigma": 1.6
            },
            "iter": 100,
            "interestParams": ['x', 'y', 'residual'],
        }

        pystanProcessor = PyStanSamplingProcessor("pystanProcessor")
        self.assertTrue(pystanProcessor.Configure(pystan_config))
        self.assertTrue(pystanProcessor.Run())
        self.assertEqual(len(pystanProcessor.results["y"]), 100)
        # Because we need this generator for the LinearFit analysis, we return the data, and not a bool
        return pystanProcessor.results

    def test_PyStanWarmup(self):
        logger.info("PyStanSampling warmup chain test")
        from morpho.processors.sampling import PyStanSamplingProcessor

        pystan_config = {
            "model_code": "model.stan",
            "input_data": {
                "slope": 1,
                "intercept": -2,
                "xmin": 1,
                "xmax": 10,
                "sigma": 1.6
            },
            "iter": 1000,
            "warmup": 900,
            "interestParams": ['x', 'y', 'residual'],
            "inc_warmup": False
        }
        pystanProcessor = PyStanSamplingProcessor("pystanProcessor")
        self.assertTrue(pystanProcessor.Configure(pystan_config))
        self.assertTrue(pystanProcessor.Run())
        self.assertEqual(len(pystanProcessor.results["y"]), 100) # iter-warmup = 1000-900 = 100

    def test_LinearFitRooFitSampler(self):
        logger.info("LinearFitRooFitSampler test")
        from morpho.processors.sampling.LinearFitRooFitProcessor import LinearFitRooFitProcessor
        from morpho.processors.plots import TimeSeries, APosterioriDistribution

        linearFit_config = {
            "iter": 10000,
            "warmup": 2000,
            "mode": "lsampling",
            "interestParams": ['a', 'b', 'width'],
            "varName": "XY",
            "fixedParams": {},
            "nuisanceParams": [],
            "paramRange": {
                "x": [-10, 10],
                "y": [-10, 50],
                "a": [-10, 10],
                "b": [-10, 10],
                "width": [0., 5.]
            },
            "n_jobs": 3
        }
        aposteriori_config = {
            "n_bins_x": 100,
            "n_bins_y": 100,
            "variables": ['a', 'b', 'width', "lp_prob"],
            "title": "aposteriori_distribution",
            "output_path": "plots"
        }
        timeSeries_config = {
            "variables": ['a', 'b', 'width'],
            "height": 1200,
            "title": "timeseries",
            "output_path": "plots"
        }
        # Definition of the processors
        aposterioriPlotter = APosterioriDistribution("posterioriDistrib")
        timeSeriesPlotter = TimeSeries("timeSeries")
        fitterProcessor = LinearFitRooFitProcessor("linearFit")

        # Configuration step
        self.assertTrue(aposterioriPlotter.Configure(aposteriori_config))
        self.assertTrue(timeSeriesPlotter.Configure(timeSeries_config))
        self.assertTrue(fitterProcessor.Configure(linearFit_config))

        # Doing things step
        fitterProcessor.data = self.test_PyStan()
        self.assertTrue(fitterProcessor.Run())
        aposterioriPlotter.data = fitterProcessor.results
        timeSeriesPlotter.data = fitterProcessor.results
        self.assertTrue(aposterioriPlotter.Run())
        self.assertTrue(timeSeriesPlotter.Run())

        def mean(numbers):
            return float(sum(numbers)) / max(len(numbers), 1)
        self.assertTrue(mean(fitterProcessor.results["a"]) > 0.5)


    def test_PyBind(self):
        logger.info("PyBind tester")
        from morpho.processors.sampling.PyBindRooFitProcessor import PyBindRooFitProcessor
        from morpho.processors.plots import Histogram, APosterioriDistribution, TimeSeries
        pybind_gene_config = {
            "varName": "XY",
            "paramRange": {
                # "x": [17000, 20000],
                "x": [-10, 10],
                # "y": [-10, 50],
                "a": [0,10],
                "b": [0, 10],
                "c": [1, 10000]
            },
            "iter": 10000,
            "fixedParams": {'a':1, 'b':1,'c':2},
            "interestParams": ['x'],
            "module_name": "myModule",
            "function_name": "myFunction",
            "mode": "generate"
        }        
        pybind_fit_config = {
            "varName": "x",
            "paramRange": {
                "x": [-10, 10],
                # "y": [-10, 50],
                "a": [0, 5],
                # "a": [18000, 19000],
                "b": [0, 5],
                "c": [0, 4]
            },
            "initValues": {
                # "y": [-10, 50],
                "a": 1,
                # "a": [18000, 19000],
                "b": 1,
                "c": 2
            },
            # "iter": 10000,
            "fixedParams": {},
            "interestParams": ['a','b','c'],
            "module_name": "myModule",
            "function_name": "myFunction",
            "binned": True,
            "mode": "fit"
        }      
        # pybind_lsampling_config = {
        #     "varName": "x",
        #     "paramRange": {
        #         "x": [-10, 10],
        #         # "y": [-10, 50],
        #         "a": [0,4],
        #         # "a": [18000, 19000],
        #         "b": [0.1, 4],
        #         "c": [1, 4]
        #     },
        #     "initValues": {
        #         # "y": [-10, 50],
        #         # "a": 1,
        #         # "a": [18000, 19000],
        #         "b": 1
        #         # "c": 2
        #     },
        #     "iter": 5000,
        #     "warmup": 1000,
        #     "fixedParams": {'a':1, 'c':2},
        #     "interestParams": ['b'],
        #     "nuisanceParams": [],
        #     "module_name": "myModule",
        #     "function_name": "myFunction",
        #     "binned": False,
        #     "n_jobs": 3,
        #     "mode": "lsampling"
        # }
        histo_config = {
            "variables": "x",
            "n_bins_x": 300,
            "output_path": "plots"
        }
        # aposteriori_config = {
        #     "n_bins_x": 100,
        #     "n_bins_y": 100,
        #     "variables": ['b', 'lp_prob'],
        #     "title": "aposteriori_distribution",
        #     "output_path": "plots"
        # }
        # timeSeries_config = {
        #     "variables": ['b', 'lp_prob'],
        #     "height": 600,
        #     "title": "timeseries",
        #     "output_path": "plots"
        # }
        sampler = PyBindRooFitProcessor("sampler")
        fitter = PyBindRooFitProcessor("fitter")
        # lsampler = PyBindRooFitProcessor("lsampler")
        myhisto = Histogram("histo")
        # timeSeriesPlotter = TimeSeries("timeSeries")
        # aposterioriPlotter = APosterioriDistribution("posterioriDistrib")
        self.assertTrue(sampler.Configure(pybind_gene_config))
        self.assertTrue(fitter.Configure(pybind_fit_config))
        # self.assertTrue(lsampler.Configure(pybind_lsampling_config))
        # self.assertTrue(timeSeriesPlotter.Configure(timeSeries_config))
        self.assertTrue(myhisto.Configure(histo_config))
        # self.assertTrue(aposterioriPlotter.Configure(aposteriori_config))
        
        self.assertTrue(sampler.Run())
        myhisto.data = sampler.data
        fitter.data = sampler.data
        # lsampler.data = sampler.data
        self.assertTrue(myhisto.Run())
        self.assertTrue(fitter.Run())
        # self.assertTrue(lsampler.Run())
        # aposterioriPlotter.data = lsampler.results
        # timeSeriesPlotter.data = lsampler.results
        # self.assertTrue(timeSeriesPlotter.Run())
        # self.assertTrue(aposterioriPlotter.Run())

    def test_GaussianSampler(self):
        logger.info("GaussianSampler test")
        from morpho.processors.sampling.GaussianSamplingProcessor import GaussianSamplingProcessor
        from morpho.processors.plots import Histogram

        gauss_config = {
            "iter": 10000
        }
        histo_config = {
            "variables": "x",
            "n_bins_x": 300,
            "output_path": "plots"
        }

        sampler = GaussianSamplingProcessor("sampler")
        myhisto = Histogram("histo")
        self.assertTrue(sampler.Configure(gauss_config))
        self.assertTrue(myhisto.Configure(histo_config))
        if not sampler.Run():
            logger.error("Error while running <sampler>")
            return False
        myhisto.data = sampler.results
        self.assertTrue(myhisto.Run())

    def test_linearModelGenerator(self):
        logger.info("LinearFitRooFitGenerator test")
        from morpho.processors.sampling.LinearFitRooFitProcessor import LinearFitRooFitProcessor
        from morpho.processors.plots import TimeSeries, APosterioriDistribution

        linearFit_config = {
            "iter": 2000,
            "warmup": 10,
            "interestParams": ['x', 'y'],
            "fixedParams": {'a': 1.,
                            'b': 1.,
                            'width': 0.2},
            "varName": "XY",
            "nuisanceParams": [],
            "paramRange": {
                "x": [-10, 10],
                "y": [-10, 50],
                "a": [-10, 10],
                "b": [-10, 10],
                "width": [0., 5.]
            },
            "n_jobs": 3,
            "mode": "generate"
        }
        aposteriori_config = {
            "n_bins_x": 100,
            "n_bins_y": 100,
            "variables": ['x', 'y'],
            "title": "aposteriori_distribution",
            "output_path": "plots"
        }
        sampler = LinearFitRooFitProcessor("sampler")
        aposterioriPlotter = APosterioriDistribution("posterioriDistrib")
        self.assertTrue(sampler.Configure(linearFit_config))
        self.assertTrue(aposterioriPlotter.Configure(aposteriori_config))
        self.assertTrue(sampler.Run())
        aposterioriPlotter.data = sampler.data
        self.assertTrue(aposterioriPlotter.Run())

    def test_GaussianRooFit(self):
        logger.info("GaussianRooFit test")
        from morpho.processors.sampling import GaussianRooFitProcessor
        from morpho.processors.plots import TimeSeries

        gaussGen_config = {
            "iter": 2000,
            "interestParams": ['x'],
            "fixedParams": {'mean': 1.,
                            'width': 0.2},
            "varName": "XY",
            "nuisanceParams": [],
            "paramRange": {
                "x": [-10, 10],
                "mean": [-10, 10],
                "width": [0., 5.]
            },
            "n_jobs": 3,
            "mode": "generate"
        }
        timeSeries_config = {
            "variables": ['x'],
            "height": 600,
            "title": "timeseries",
            "output_path": "plots"
        }
        gaussSampler_config = {
            "iter": 10000,
            "warmup": 5000,  # there is not enough warmup, this is to show the convergence of the chain
            "interestParams": ['mean', 'width'],
            "fixedParams": {},
            "varName": "XY",
            "nuisanceParams": [],
            "paramRange": {
                "x": [-10, 10],
                "mean": [-10, 10],
                "width": [0., 5.]
            },
            "n_jobs": 3,
            "mode": "lsampling"
        }
        aposteriori_config = {
            "n_bins_x": 100,
            "n_bins_y": 100,
            "variables": ['mean', 'width'],
            "title": "aposteriori_distribution_gaussSampling",
            "output_path": "plots"
        }
        fitter_config = {
            "iter": 10000,
            "warmup": 5000,  # there is not enough warmup, this is to show the convergence of the chain
            "interestParams": ['mean', 'width'],
            "fixedParams": {},
            "varName": "XY",
            "nuisanceParams": [],
            "paramRange": {
                "x": [-10, 10],
                "mean": [-10, 10],
                "width": [0., 5.]
            },
            "n_jobs": 3,
            "mode": "fit"
        }
        sampler = GaussianRooFitProcessor("sampler")
        lsampler = GaussianRooFitProcessor("lsampler")
        fitter = GaussianRooFitProcessor("fitter")
        timeSeriesPlotter = TimeSeries("timeSeries")
        aPostPlotter = TimeSeries("aPostPlotter")

        self.assertTrue(sampler.Configure(gaussGen_config))
        self.assertTrue(lsampler.Configure(gaussSampler_config))
        self.assertTrue(fitter.Configure(fitter_config))
        self.assertTrue(timeSeriesPlotter.Configure(timeSeries_config))
        self.assertTrue(aPostPlotter.Configure(aposteriori_config))

        # Run fake data generator and plot data timeseries
        self.assertTrue(sampler.Run())
        timeSeriesPlotter.data = sampler.data
        lsampler.data = sampler.data
        fitter.data = sampler.data
        self.assertTrue(timeSeriesPlotter.Run())
        # Run lsampler generator and plot timeseries
        self.assertTrue(lsampler.Run())
        aPostPlotter.data = lsampler.results
        self.assertTrue(aPostPlotter.Run())

        # Run fitter
        fitter.data = sampler.data
        self.assertTrue(fitter.Run())
        logger.info("Fit Results: {}".format(fitter.result))


if __name__ == '__main__':
    unittest.main()
