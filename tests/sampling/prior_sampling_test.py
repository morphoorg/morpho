'''
This scripts aims at testing the PriorSamplingProcessor by generating sampled values.
Author: T. E. Weiss
Date: May 15 2020
'''

import unittest

from morpho.utilities import morphologging
logger = morphologging.getLogger(__name__)
from morpho.processors.sampling import PriorSamplingProcessor

import numpy as np

class PriorSamplingTests(unittest.TestCase):

    def test_prior_dist(self):
        logger.info("Testing sampling with five prior distribution types")
        
        prior_sampler_config = {
        "fixed_inputs": {
            'x_fixed': 0,
            'y_fixed': -1
            },
        "priors": [
            {'name': 'A', 'prior_dist': 'normal', 'prior_params': [10, 0.5]},
            {'name': 'B', 'prior_dist': 'gamma', 'prior_params': [1.135, 0.4344]},
            {'name': 'C', 'prior_dist': 'beta', 'prior_params': [55, 17]},
            {'name': 'D', 'prior_dist': 'loguniform', 'prior_params':[0, 4]},
            {'name': 'E', 'prior_dist': 'randint', 'prior_params':[0, 2]}
            ]
        }
    
        priorSampler = PriorSamplingProcessor("sample")
        self.assertTrue(priorSampler.Configure(prior_sampler_config))
        self.assertTrue(priorSampler.Run())
        self.assertEqual(len(priorSampler.results), 7)
    
    
    def test_normal_prior_properties(self):
        logger.info("Testing normal prior distribution sampling")
        
        prior_sampler_config2 = {
            "priors": [{'name':str(i), 'prior_dist':'normal', 'prior_params':[0, 1]} for i in range(1000)],
            "verbose": False
        }
        
        priorSampler = PriorSamplingProcessor("sample")
        self.assertTrue(priorSampler.Configure(prior_sampler_config2))
        self.assertTrue(priorSampler.Run())
        
        logger.info("Mean of sampled values is {}. Is it near 0?".format(np.mean(list(priorSampler.results.values()))))
        logger.info("Standard deviation of sampled values is {}. Is it near 1?".format(np.std(list(priorSampler.results.values()))))
    

if __name__ == '__main__':
    unittest.main()
    
