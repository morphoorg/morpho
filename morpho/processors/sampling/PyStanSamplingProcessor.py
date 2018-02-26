'''
PyStan sampling processor
'''

from __future__ import absolute_import

import os
import random
import re
from hashlib import md5
import pystan

from morpho.utilities import morphologging, reader, pystanLoader
from morpho.processors import BaseProcessor
logger=morphologging.getLogger(__name__)
logger_stan=morphologging.getLogger('pystan')

__all__ = []
__all__.append(__name__)

class PyStanSamplingProcessor(BaseProcessor):
    '''
    Sampling processor that will call PyStan
    '''

    def _stan_cache(self):
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

        # if (args.force_restart):
        logger.debug("Forced to create Stan cache!")
        # self.stanModel = pystan.StanModel(model_code=theModel)
        # if not args.no_cache:
        #     logger.debug("Saving Stan cache in {}".format(cache_fn))
        #     with open(cache_fn, 'wb') as f:
        #         pickle.dump(sm, f)
        # else:
        import pickle
        try:
            logger.debug("Trying to load cached StanModel")
            self.stanModel = pickle.load(open(cache_fn, 'rb'))
        except:
            logger.debug("None exists -> creating Stan cache")
            self.stanModel = pystan.StanModel(model_code=theModel)
            # if not args.no_cache:
            logger.debug("Saving Stan cache in {}".format(cache_fn))
            with open(cache_fn, 'wb') as f:
                pickle.dump(self.stanModel, f)
        else:
            logger.debug("Using cached StanModel: {}".format(cache_fn))

        # if sa.out_cache_fn is not None:
        #     logger.debug("Saving cache file to {}".format(self.out_cache_fn))
        #     cache_name_file = open(sa.out_cache_fn,'w+')
        #     cache_name_file.write(cache_fn)

    def _run_stan(self, *args, **kwargs):
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
        return self.stanModel.sampling(**kwargs)
# return stan_results

    def Configure(self, params):
        logger.info("Configure with {}".format(params))
        # print(self, params)
        self.params = params
        self.model_code = reader.read_param(params, 'model_code', 'required')
        self.function_files_location = reader.read_param(params, 'function_files_location', None)
        self.model_name = reader.read_param(params, 'model_name', None)
        self.cache_dir = reader.read_param(params, 'cache_dir', '.')
        self.input_data = reader.read_param(params, 'input_data', 'required')
        self.iterations = reader.read_param(params, 'iterations', 'required')
        self.warmup = int(reader.read_param(params, 'warmup', self.iterations/2))
        self.chains = int(reader.read_param(params, 'chain', 1))
        self.n_jobs = int(reader.read_param(params, 'n_jobs',-1)) # number of jobs to run (-1: all, 1: good for debugging)
        self.interestParams = reader.read_param(params, 'interestParams',[])
        # Adding a seed based on extra arguments, current time
        # if isinstance(args.seed,(int,float,str)):
        #     self.seed=int(args.seed)
        # elif args.noautoseed:
        self.seed = int(random.random()*1000000000) # seed based on random.random and the current system time
        logger.debug("Autoseed activated")
        # else:
            # self.seed = int(reader.read_param(yd, 'stan.run.seed', None))
        logger.debug("seed = {}".format(self.seed))

        self.thin = reader.read_param(params, 'stan.run.thin', 1)
        self.init_per_chain = reader.read_param(params, 'stan.run.init', '')
        # self.init = self.init_Stan_function()
        # if isinstance(reader.read_param(params, 'stan.run.control', None),dict):
        #     self.control = reader.read_param(params, 'stan.run.control', None)
        # else:
        #     if reader.read_param(params, 'stan.run.control', None) is not None:
        #         logger.debug("stan.run.control should be a dict: {}",str(reader.read_param(yd, 'stan.run.control', None)))

    def Run(self):
        logger.info("Run...")
        self._stan_cache()
        stan_results = self._run_stan()
        logger.debug("Stan Results:\n"+str(stan_results))
        # Put the data into a nice dictionary
        return pystanLoader.extract_data_from_outputdata(self.__dict__,stan_results)

