'''
PyStan sampling processor
'''

from __future__ import absolute_import

import json
import os

from morpho.utilities import morphologging
from morpho.processors import BaseProcessor
logger=morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)

class PyStanSamplingProcessor(BaseProcessor):
    '''
    Sampling processor that will call PyStan
    '''
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        return

    def _stan_cache():
        '''
        Create and cache stan model, or access previously cached model
        '''
        theModel = open(self.model_code,'r+').read()
        match =  re.findall(r'\s*include\s*=\s*(?P<function_name>\w+)\s*;*',theModel)
        if self.function_files_location is not None:
            logger.debug('Looking for the functions to import in {}'.format(self.function_files_location))
            from os import listdir
            from os.path import isfile, join
            onlyfiles = [f for f in listdir(self.function_files_location) if isfile(join(self.function_files_location, f))]
        else:
            logger.debug('No functions file location given')
            onlyfiles = []
        for matches in match:
            found = False
            for filename in onlyfiles:
                if filename.endswith('.functions'):
                    key = filename[:-10]
                elif  filename.endswith('.stan'):
                    key = filename[:-5]
                else:
                    continue
                if (key==matches):
                    StanFunctions = open(self.function_files_location+'/'+filename,'r+').read()
                    theModel = re.sub(r'\s*include\s*=\s*'+matches+'\s*;*\n',StanFunctions, theModel, flags=re.IGNORECASE)
                    found = True
                    logger.debug('Function file <{}> to import was found'.format(matches))
                    continue
            if found == False:
                logger.critical('A function <{}> to import is missing'.format(matches))
        logger.debug('Import function files: complete')
                
        code_hash = md5(theModel.encode('ascii')).hexdigest()
        if self.model_name is None:
            cache_fn = '{}/cached-model-{}.pkl'.format(self.cache_dir, code_hash)
        else:
            cache_fn = '{}/cached-{}-{}.pkl'.format(self.cache_dir, self.model_name, code_hash)

        cdir = os.path.dirname(cache_fn)
        if not os.path.exists(cdir):
            os.makedirs(cdir)
            logger.info("Creating 'cache' folder: {}".format(cdir))

        if (args.force_restart):
            logger.debug("Forced to create Stan cache!")
            sm = pystan.StanModel(self.model_code=theModel)
        if not args.no_cache:
            logger.debug("Saving Stan cache in {}".format(cache_fn))
            with open(cache_fn, 'wb') as f:
                pickle.dump(sm, f)
        else:
            try:
                logger.debug("Trying to load cached StanModel")
                sm = pickle.load(open(cache_fn, 'rb'))
            except:
                logger.debug("None exists -> creating Stan cache")
                sm = pystan.StanModel(self.model_code=theModel)
                if not args.no_cache:
                    logger.debug("Saving Stan cache in {}".format(cache_fn))
                    with open(cache_fn, 'wb') as f:
                        pickle.dump(sm, f)
            else:
                logger.debug("Using cached StanModel: {}".format(cache_fn))

        if sa.out_cache_fn is not None:
            logger.debug("Saving cache file to {}".format(sa.out_cache_fn))
            cache_name_file = open(sa.out_cache_fn,'w+')
            cache_name_file.write(cache_fn)

    def run_stan():
        logger.info("Starting the sampling")
        text = "Parameters: \n"
        for key, value in kwargs.items():
            if key != "data" and key != "init" :
                text = text + "{}\t{}\n".format(key,value)
            elif key == "data":
                text = text + "data\t[...]\n"
            elif key == "init":
                text = text + "init\t[...]\n"
        logger.info(text)
        # returns the arguments for sampling and the result of the sampling
        return kwargs, sm.sampling(**kwargs)
return stan_results

    def Configure(self, params):
        print(self, params)
        self.params = params
        self.model_code = self.read_param(params, 'model_code', 'required')
        self.function_files_location = self.read_params(params, 'function_files_location', None)
        self.model_name = self.read_params(params, 'model_name', None)
        self.cache_dir = self.read_params(params, 'cache_dir', '.')
        self.input_data = self.read_param(params, 'input_data', 'required')
        self.iterations = self.read_param(params, 'iterations', 'required')
        self.warmup = int(self.read_param(yd, 'stan.run.warmup', self.iter/2))
        self.chains = int(self.read_param(yd, 'stan.run.chain', 4))
        self.n_jobs = int(self.read_param(yd, 'stan.run.n_jobs',-1)) # number of jobs to run (-1: all, 1: good for debugging)
        # Adding a seed based on extra arguments, current time
        if isinstance(args.seed,(int,float,str)):
            self.seed=int(args.seed)
        elif args.noautoseed:
            self.seed = int(random.random()*1000000000) # seed based on random.random and the current system time
            logger.debug("Autoseed activated")
        else:
            self.seed = int(self.read_param(yd, 'stan.run.seed', None))
        logger.debug("seed = {}".format(self.seed))

        self.thin = self.read_param(yd, 'stan.run.thin', 1)
        self.init_per_chain = self.read_param(yd, 'stan.run.init', '')
        self.init = self.init_Stan_function()
        if isinstance(self.read_param(yd, 'stan.run.control', None),dict):
            self.control = self.read_param(yd, 'stan.run.control', None)
        else:
            if self.read_param(yd, 'stan.run.control', None) is not None:
                logger.debug("stan.run.control should be a dict: {}",str(self.read_param(yd, 'stan.run.control', None)))

    def Run(self):
        stan_model = self.stan_cache()
        stan_results = self.run_stan(stan_model)
        self.params = self.add_param(self.params, "stan_results", stan_results)
        return self.params

