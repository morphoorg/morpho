'''
This scripts aims at testing IO processors by reading/writing files.
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
        
        linearFit_config = {
            "iter": 100,
            "interestParams": ['slope','intercept','width'],
            "varName": "y",
            "nuisanceParams": [],
            "paramRange": {
                "x":[0,10],
                "y":[0,10],
                "a":[0,10],
                "b":[0,10]
            }
        }


        fitterProcessor = LinearFitRooFitLikelihoodProcessor("linearFit")
        fitterProcessor.Configure(linearFit_config)
        fitterProcessor.data = self.test_PyStan()
        fitterProcessor.Run()
        

if __name__ == '__main__':
    unittest.main()