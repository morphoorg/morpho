'''
Processor for sampling inputs to a data generator from priors.
Useful for sensitivity analyses.

Authors: T. E. Weiss
Date: May 2020
'''

from __future__ import absolute_import

import numpy as np

from morpho.utilities import morphologging, reader
from morpho.processors import BaseProcessor
logger = morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)


class PriorSamplingProcessor(BaseProcessor):
    '''
    Input:
        priors: list of dictionaries with the following required keys:
            'name' - str; parameter name
            'prior_dist' - str; name of prior distribution to sample from (e.g. 'gamma')
            'prior_params' - list of values parameterizing prior, following numpy conventions (e.g. [1, 2] for beta prior with k=1 and theta=2)
        fixed_inputs: (optional) dictionary containing any inputs to the next processor/data generator which will *not* be sampled from priors

    Results:
        sampled_inputs: dictionary containing values sampled from priors as designated in the priors dict, as well as the keys/values in the fixed_inputs dict
    '''
    def InternalConfigure(self,priors):
        self.priors = reader.read_param(priors,'priors',{})
        self.fixed_inputs = reader.read_param(fixed_inputs,'fixed_inputs',{})
        return True
    
    def _sample_inputs():
        logger.info("Sampling values from priors")
        sampled_inputs = self.fixed_inputs
        
        for sample_dict in self.priors:
            name = sample_dict['name']
            dist_error = 'Sampling for {} distribution is not yet implemented'.format(sample_dict['prior_dist'])
            
            #One can use the name of a fixed input to define a prior parameter
            for i in range(len(sample_dict['prior_params'])):
                x = sample_dict['prior_params'][i]
                if type(x)==str:
                    sample_dict['prior_params'][i]=self.fixed_inputs[x]

            #Performing the sampling
            rand = self._draw_random_sample(sample_dict, dist_error)
            sampled_inputs[name] = rand
            logger.info('Sampled value of {}: {}'.format(name, rand))
            
        return sampled_inputs

    def _draw_random_sample(sample_dict, dist_error):
        np.random.seed()
        p, vals = sample_dict['prior_dist'], sample_dict['prior_params']
        if p == 'normal':
            randarray = np.random.normal(vals[0], vals[1], 1)
            rand = randarray[0]
        elif p == 'lognormal':
            rand = np.random.lognormal(vals[0], vals[1], 1)[0]
        elif p == 'beta':
            rand = np.random.beta(vals[0], vals[1], 1)[0]
        elif p == 'gamma':
            rand = np.random.gamma(vals[0], vals[1], 1)[0]
        elif p == 'randint':
            rand = np.random.randint(vals[0], high=vals[1]+1)
        elif p == 'loguniform':
            rand = np.power(10, np.random.uniform(vals[0], vals[1], 1))[0]
        else:
            logger.debug(dist_error)
            return None
        return rand

    def InternalRun(self):
        sampled_inputs = self._sample_inputs()
        if sampled_inputs == self.fixed_inputs:
            logger.debug("No inputs were sampled from priors")
        return sampled_inputs

