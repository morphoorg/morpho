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
        if not pystanProcessor.Configure(pystan_config):
            logger.error("Error while configuring <pystanProcessor>")
            return False
        if not pystanProcessor.Run():
            logger.error("Error while running <pystanProcessor>")
            return False
        self.assertEqual(len(pystanProcessor.results["y"]), 100)
        # Because we need this generator for the LinearFit analysis, we return the data, and not a bool
        return pystanProcessor.results

    def test_LinearFitRooFitSampler(self):
        logger.info("LinearFitRooFitSampler test")
        from morpho.processors.sampling import LinearFitRooFitLikelihoodProcessor
        from morpho.processors.plots import TimeSeries, APosterioriDistribution

        linearFit_config = {
            "iter": 10000,
            "warmup": 2000,
            "interestParams": ['a', 'b', 'width'],
            "varName": "XY",
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
        fitterProcessor = LinearFitRooFitLikelihoodProcessor("linearFit")

        # Configuration step
        aposterioriPlotter.Configure(aposteriori_config)
        timeSeriesPlotter.Configure(timeSeries_config)
        if not fitterProcessor.Configure(linearFit_config):
            logger.error("Error while configuring <linearFit>")
            return False

        # Doing things step
        fitterProcessor.data = self.test_PyStan()
        if not fitterProcessor.Run():
            logger.error("Error while running <linearFit>")
            return False
        aposterioriPlotter.data = fitterProcessor.results
        timeSeriesPlotter.data = fitterProcessor.results
        aposterioriPlotter.Run()
        timeSeriesPlotter.Run()

        def mean(numbers):
            return float(sum(numbers)) / max(len(numbers), 1)
        self.assertTrue(mean(fitterProcessor.results["a"]) > 0.5)

    def test_GaussianSampler(self):
        logger.info("GaussianSampler test")
        from morpho.processors.sampling import GaussianSamplingProcessor
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
        sampler.Configure(gauss_config)
        myhisto.Configure(histo_config)
        if not sampler.Run():
            logger.error("Error while running <sampler>")
            return False
        myhisto.data = sampler.results
        myhisto.Run()

    def test_linearModelGenerator(self):
        logger.info("LinearFitRooFitGenerator test")
        from morpho.processors.sampling import LinearFitRooFitProcessor
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
            "mode": "generator"
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
        sampler.Configure(linearFit_config)
        aposterioriPlotter.Configure(aposteriori_config)
        sampler.Run()
        aposterioriPlotter.data = sampler.data
        aposterioriPlotter.Run()




if __name__ == '__main__':
    unittest.main()
