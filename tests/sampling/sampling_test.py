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
        from morpho.processors.sampling import PyStanSamplingProcessor

        pystan_config = {
            "model_code": "model.stan",
            "input_data": {
                "slope": 1,
                "intercept":-2,
                "xmin":1,
                "xmax":10,
                "sigma": 1.6
            },
            "iter": 100,
            "interestParams": ['x','y','residual'],
        }

        pystanProcessor = PyStanSamplingProcessor("pystanProcessor")
        pystanProcessor.Configure(pystan_config)
        result = pystanProcessor.Run()
        self.assertEqual(len(result["y"]),100)
        return result

    def test_LinearFitRooFitSampler(self):
        from morpho.processors.sampling import LinearFitRooFitLikelihoodProcessor
        from morpho.processors.plots import TimeSeries, APosterioriDistribution
        
        linearFit_config = {
            "iter": 10000,
            "warmup": 500,
            "interestParams": ['a','b','width'],
            "varName": "XY",
            "nuisanceParams": [],
            "paramRange": {
                "x":[-10,10],
                "y":[-10,50],
                "a":[-10,10],
                "b":[-10,10],
                "width":[0.,5.]
            },
            "n_jobs": 3
        }
        aposteriori_config = {
            "n_bins_x": 100,
            "n_bins_y": 100,
            "data": ['a','b','width',"lp_prob"],
            "title": "aposteriori_distribution",
            "output_path": "plots"
        }
        timeSeries_config = {
            "data": ['a','b','width'],
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
        fitterProcessor.Configure(linearFit_config)

        # Doing things step
        fitterProcessor.data = self.test_PyStan()
        result = fitterProcessor.Run()
        aposterioriPlotter.data = result
        timeSeriesPlotter.data = result
        aposterioriPlotter.Run()
        timeSeriesPlotter.Run()

        import numpy as np

        self.assertTrue(np.mean(result["a"])>0.5)

        

if __name__ == '__main__':
    unittest.main()