'''
PyStan sampling processor
Authors: J. Formaggio, J. Johnston, M. Guigue, T. Weiss
Date: 06/26/18
'''

from __future__ import absolute_import

import os
import random
import re
from hashlib import md5
from inspect import getargspec
from datetime import datetime

try:
    import pystan
except ImportError:
    pass

from morpho.utilities import morphologging, reader, pystanLoader
from morpho.processors import BaseProcessor
from morpho.processors.sampling import PyStanBaseProcessor
logger = morphologging.getLogger(__name__)
logger_stan = morphologging.getLogger('pystan')

__all__ = []
__all__.append(__name__)


class PyStanSamplingProcessor(PyStanBaseProcessor):
    '''
    Sampling processor that will call PyStan.

    Parameters:
        model_code (required): location of the Stan model
        function_files_location: location of the Stan functions
        model_name: name of the cached model
        cache_dir: location of the cache folder (containing cached models)
        input_data: dictionary containing model input data
        iter (required): total number of iterations (warmup and sampling)
        warmup: number of warmup iterations (default=iter/2)
        chain: number of chains (default=1)
        n_jobs: number of parallel cores running (default=1)
        interestParams: parameters to be saved in the results variable
        no_cache: don't create cache
        force_recreate: force the cache regeneration
        init: initial values for the parameters
        control: PyStan sampling settings

    Input:
        data: dictionary containing model input data

    Results:
        results: dictionary containing the result of the sampling of the parameters of interest
    '''
    
    def __init__(self, name):
        super().__init__(name)
        self._data = {}

    def _run_stan(self, *args, **kwargs):
        logger.info("Starting the sampling")
        text = "Parameters: \n"
        for key, value in kwargs.items():
            if key != "data" and key != "init":
                text = text + "{}\t{}\n".format(key, value)
            elif key == "data":
                text = text + "data\t[...]\n"
            elif key == "init":
                text = text + "init\t[...]\n"
        logger.info(text)
        # returns the arguments for sampling and the result of the sampling
        stan_results = self.stanModel.sampling(**(kwargs))
        # Put results into a nice dictionary
        self.results = pystanLoader.extract_data_from_outputdata(
            self.__dict__, stan_results)
        return True

