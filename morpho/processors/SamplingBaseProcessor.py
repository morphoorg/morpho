'''
Base processor for sampling-type operations
'''

from __future__ import absolute_import

import json
import os

from morpho.utilities import morphologging
logger=morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)

class SamplingBaseProcessor:
    '''
    Base Processor for Sampling operations.
    Samplers should be implemented in a child class where the specificities are encoded using overloaded methods.
    '''

    def __init__(self, name, *args, **kwargs):
        self.__name = name
        return

    def set_data(self, input):
        self.data = input

    def set_model(self, input = ["file1.stan"]):
        self.model_files = input

    def Configure(self, input):
        '''
        This method should be called by nymph to configure the processor, e.g. define the number of samples.
        It uses the content of the input to get all the required information.
        It might build the model here (if necessary).
        An example of the input dictionary is:
            algorithm: "NUTS"
            iter: 4000
            warmup: 1000
            chain: 12
            n_jobs: 2
            init:
                - slope : 2.0
                  intercept : 1.0
                  sigma: 1.0
        '''
        logger.error("Default Configure method: need to implement your own")
        raise

    def Run(self):
        '''
        This is where the sampler magic happens: we define a method that loads/build/configure the model and one that execute it.
        These methods depend on the actual sampler used: 
            - for PyStan, the model consists in an object called pystan.StanModel using the models files defined by:
            ``` sm = pystan.StanModel(file='8schools.stan') ```
            The sampling part would consist in a command like:
            ``` sm.sampling(data=schools_dat, iter=10000, chains=4) ```
            - for RooFit, the model would be a python function/attribute in a python script.
            The sampling would consist in executing this function after giving it some data and parameters
        In both cases, the output file should be a SamplingData object.
        An example of possible content is:
        
            self.model = self.create_model(self)
            self.samples = self.sample_model(self)
            return self.samples
        '''
        logger.error("Default Run method: need to implement your own")
        raise 


