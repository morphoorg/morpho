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
import numpy

try:
    import pystan
except ImportError:
    pass

from morpho.utilities import morphologging, reader, pystanLoader, stanConvergenceChecker
from morpho.processors import BaseProcessor
from morpho.processors.plots import Histo2dDivergence
logger = morphologging.getLogger(__name__)
logger_stan = morphologging.getLogger('pystan')

__all__ = []
__all__.append(__name__)


class PyStanSamplingProcessor(BaseProcessor):
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
        warmup_inc: include warmup part of the chains (default=True)
        chain: number of chains (default=1)
        n_jobs: number of parallel cores running (default=1)
        interestParams: parameters to be saved in the results variable
        no_cache: don't create cache
        force_recreate: force the cache regeneration
        init: initial values for the parameters
        control: PyStan sampling settings
        no_diagnostics: Prevent diagnostics plots from being generated (default=False)
        diagnostics_folder: Path to folder to store diagnostics (default=".")

    Input:
        data: dictionary containing model input data

    Results:
        results: dictionary containing the result of the sampling of the parameters of interest
        results_c: dictionary containing the result of the sampling of the parameters of interest (without the warmup chain)
    '''
    @property
    def data(self):
        return self._data
    
    @property
    def results_c(self):
        n_warmup=-1
        for i_sample, value in results["is_sample"].items():
            if value == 0:
                n_warmup = i_sample
                
        results_c = dict()
        for a_key, a_value in results.items():
            result_c.update({a_key: a_value[n_warmup+1:]})
        return result_c

    @data.setter
    def data(self, input_dict):
        if isinstance(input_dict, dict):
            for a_key, a_value in input_dict.items():
                reader.add_dict_param(self.data, a_key, a_value)
        else:
            logger.warning("Not a dict: {}".format(input_dict))

    def __init__(self, name):
        super().__init__(name)
        self._data = {}

    def gen_arg_dict(self):
        '''
        Generate a dictionary as paramter if the pystan.sampling method
        '''
        d = self.__dict__
        sa = getargspec(pystan.StanModel.sampling)
        output_dict = {k: d[k] for k in (sa.args) if k in d}
        # We need to manually add the data to the dictionary because of the setter...
        output_dict.update({'data': self.data})
        return output_dict

    def _init_Stan_function(self):
        if isinstance(self.init_per_chain, list):
            # init_per_chain is a list of dictionaries
            if self.chains > 1 and len(self.init_per_chain) == 1:
                dict_list = [self.init_per_chain[0]] * self.chains
                return dict_list
            elif len(self.init_per_chain) == self.chains:
                return self.init_per_chain
            else:
                logger.error(
                    'Number of chains is not equal to the size of the list of dictionaries')
                return self.init_per_chain
        elif isinstance(self.init_per_chain, dict):
            # init_per_chain is a dictionary
            if self.chains > 1:
                return [self.init_per_chain] * self.chains
            else:
                return [self.init_per_chain]
        else:
            return self.init_per_chain

    def _get_data_lists_size(self):
        '''
        Parse the data and look for lists: if one is found, compute its size
        and add it to the self.data
        '''
        additional_dict = {}
        for key, value in self.data.items():
            if isinstance(value, list):
                list_size_name = "dim__{}".format(key)
                additional_dict.update({list_size_name: len(value)})
            if type(value) is numpy.ndarray:
                list_size_name = "dim__{}".format(key)
                additional_dict.update({list_size_name: int(value.size)})
        self.data.update(additional_dict)

    def _stan_cache(self):
        '''
        Create and cache stan model, or access previously cached model
        '''
        theModel = open(self.model_code, 'r+').read()
        match = re.findall(
            r'\s*include\s*=\s*(?P<function_name>\w+)\s*;*', theModel)
        if self.function_files_location is not None:
            logger.debug('Looking for the functions to import in {}'.format(
                self.function_files_location))
            from os import listdir
            from os.path import isfile, join
            onlyfiles = [f for f in listdir(self.function_files_location) if isfile(
                join(self.function_files_location, f))]
        else:
            logger.debug('No functions file location given')
            onlyfiles = []
        for matches in match:
            found = False
            for filename in onlyfiles:
                if filename.endswith('.functions'):
                    key = filename[:-10]
                elif filename.endswith('.stan'):
                    key = filename[:-5]
                else:
                    continue
                if (key == matches):
                    StanFunctions = open(
                        self.function_files_location+'/'+filename, 'r+').read()
                    theModel = re.sub(r'\s*include\s*=\s*'+matches+'\s*;*\n',
                                      StanFunctions, theModel, flags=re.IGNORECASE)
                    found = True
                    logger.debug(
                        'Function file <{}> to import was found'.format(matches))
                    continue
            if not found:
                logger.critical(
                    'A function <{}> to import is missing'.format(matches))
        logger.debug('Import function files: complete')

        code_hash = md5(theModel.encode('ascii')).hexdigest()
        if self.model_name is None:
            cache_fn = '{}/cached-model-{}.pkl'.format(
                self.cache_dir, code_hash)
        else:
            cache_fn = '{}/cached-{}-{}.pkl'.format(
                self.cache_dir, self.model_name, code_hash)
        # Cache creation and saving?
        if self.force_recreate:
            logger.debug("Forced to recreate Stan cache!")
            self._create_and_save_model(theModel, cache_fn)
        else:
            import pickle
            try:
                logger.debug("Trying to load cached StanModel")
                self.stanModel = pickle.load(open(cache_fn, 'rb'))
            except:
                logger.debug("None exists -> creating Stan cache")
                self._create_and_save_model(theModel, cache_fn)
            else:
                logger.debug("Using cached StanModel: {}".format(cache_fn))

    def _create_and_save_model(self, theModel, cache_fn):
        self.stanModel = pystan.StanModel(model_code=theModel)
        if not self.no_cache:
            cdir = os.path.dirname(cache_fn)
            if not os.path.exists(cdir):
                os.makedirs(cdir)
                logger.info("Creating 'cache' folder: {}".format(cdir))
            logger.debug("Saving Stan cache in {}".format(cache_fn))
            import pickle
            with open(cache_fn, 'wb') as f:
                pickle.dump(self.stanModel, f)

    def _run_stan(self, *args, **kwargs):
        logger.info("Starting the sampling")
        text = "Parameters: \n"
        for key, value in kwargs.items():
            if key != "data" and key != "init":
                text = text + "{}\t{}\n".format(key, value)
            elif key == "data" or key == "init":
                text = text + "{}\t[...]\n".format(key)
        logger.info(text)
        # returns the arguments for sampling and the result of the sampling
        return self.stanModel.sampling(**(kwargs))
        # return self.stanModel.sampling(**(self.gen_arg_dict()))

    def _store_diagnostics(self, stan_results):
        # Print diagnostics
        convergence_diagnostics = stanConvergenceChecker.check_all_diagnostics(stan_results)
        if convergence_diagnostics[0]:
            logger.warn("\n"+convergence_diagnostics[1])
        else:
            logger.info("\n"+convergence_diagnostics[1])
        if not os.path.exists(self.diagnostics_folder):
            os.makedirs(self.diagnostics_folder)
        f = open(self.diagnostics_folder+"/divergence_checks.txt", 'w')
        f.write(convergence_diagnostics[1])
        f.close()

        # Plot 2D grid of divergence plots
        divConfig = {"n_bins_x": 100,
                     "n_bins_y": 100,
                     "variables": self.interestParams + ["lp_prob"],
                     "title": "divergence_2d_histo",
                     "output_path": self.diagnostics_folder}
        divProcessor = Histo2dDivergence("2dDivergence")
        divProcessor.Configure(divConfig)
        divProcessor.data = self.results
        divProcessor.Run()
        return

    def InternalConfigure(self, params):
        self.params = params
        self.model_code = reader.read_param(params, 'model_code', 'required')
        self.function_files_location = reader.read_param(
            params, 'function_files_location', None)
        self.model_name = reader.read_param(params, 'model_name', "anon_model")
        self.cache_dir = reader.read_param(params, 'cache_dir', '.')
        self.data = reader.read_param(params, 'input_data', {})
        self.iter = reader.read_param(params, 'iter', 'required')
        self.warmup = int(reader.read_param(params, 'warmup', self.iter/2))
        self.inc_warmup = int(reader.read_param(params, 'inc_warmup', True))
        self.chains = int(reader.read_param(params, 'chain', 1))
        # number of jobs to run (-1: all, 1: good for debugging)
        self.n_jobs = int(reader.read_param(params, 'n_jobs', -1))
        self.interestParams = reader.read_param(params, 'interestParams', [])
        self.no_cache = reader.read_param(params, 'no_cache', False)
        self.force_recreate = reader.read_param(
            params, 'force_recreate', False)
        self.seed = random.seed(datetime.now())
        # logger.debug("Autoseed activated")
        logger.debug("seed = {}".format(self.seed))

        # self.thin = reader.read_param(params, 'thin', 1)
        self.init_per_chain = reader.read_param(params, 'init', '')

        self.init = self._init_Stan_function()
        if isinstance(reader.read_param(params, 'control', None), dict):
            self.control = reader.read_param(params, 'control', None)
        else:
            if reader.read_param(params, 'control', None) is not None:
                logger.debug("stan.run.control should be a dict: {}", str(reader.read_param(yd, 'control', None)))
        self.no_diagnostics = reader.read_param(params, 'no_diagnostics', False)
        self.diagnostics_folder = reader.read_param(params, 'diagnostics_folder', "./stan_diagnostics")
        return True

    def InternalRun(self):
        self._get_data_lists_size()
        self._stan_cache()
        stan_results = self._run_stan(**(self.gen_arg_dict()))
        logger.debug("Stan Results:\n"+str(stan_results))
        # Put the data into a nice dictionary
        self.results = pystanLoader.extract_data_from_outputdata(
            self.__dict__, stan_results)
        # Store convergence checks
        if not self.no_diagnostics:
            self._store_diagnostics(stan_results)
        else:
            logger.info("No diagnostics plots produced")
        return True
