#!/usr/bin/env python

#
# morpho.py
#
# author: j.n. kofron <jared.kofron@gmail.com>
#

from __future__ import absolute_import



import os,sys
reload(sys)
sys.setdefaultencoding("utf-8")


import logging
logger = logging.getLogger('morpho.py')
logger.setLevel(logging.DEBUG)
base_format = '%(asctime)s[%(levelname)-8s] %(name)s(%(lineno)d) -> %(message)s'
logging.basicConfig(format=base_format, datefmt='%m/%d/%Y %H:%M:%S')


import time
import fileinput
import json
import pystanLoad as pyL
import re
import random

import pystan
from pystan import stan
from yaml import load as yload
from argparse import ArgumentParser
from inspect import getargspec

import pickle
from hashlib import md5
import importlib

class morpho(object):
    def read_param(self, yaml_data, node, default):
        data = yaml_data
        xpath = node.split('.')
        try:
            for path in xpath:
                data = data[path]
        except Exception as exc:
            if default == 'required':
                err = """FATAL: Configuration parameter {0} required but not\
                provided in config file!
                """.format(node)
                logger.debug(err)
                raise exc
            else:
                data = default
        return data

    def gen_arg_dict(self):
        d = self.__dict__
        sca = getargspec(stan_cache)
        sa = getargspec(stan)
        return {k: d[k] for k in (sa.args + sca.args) if k in d}

    def init_Stan_function(self):
        if isinstance(self.init_per_chain,list): # and self.init_per_chain.GetType().IsGenericType and self.init_per_chain.GetType().GetGenericTypeDefinition().IsAssignableFrom(typeof(List<>)):
            # init_per_chain is a list of dictionaries
            if self.chains >1 and len(self.init_per_chain)==1:
                dict_list = [self.init_per_chain[0]] * self.chains
                return dict_list
            elif len(self.init_per_chain)==self.chains :
                return self.init_per_chain
            else:
                logger.error('Number of chains is not equal to the size of the list of dictionaries')
                return self.init_per_chain
        elif isinstance(self.init_per_chain,dict): # and self.init_per_chain.GetType().IsGenericType and self.init_per_chain.GetType().GetGenericTypeDefinition().IsAssignableFrom(typeof(Dictionary<,>)):
            # init_per_chain is a dictionary
            if self.chains >1:
                return [self.init_per_chain] * self.chains
            else:
                return [self.init_per_chain]
        else:
            return self.init_per_chain

    def get_do_Stan(self):
        if self.do_stan:
            return True
        else:
            return False
    def get_do_pp(self):
        if self.do_postprocessing:
            return True
        else:
            return False
    def get_do_plots(self):
        if self.do_plots:
            return True
        else:
            return False
    def get_wait(self):
        if self.wait:
            return True
        else:
            return False

    def __init__(self, yd):
        try:
            # Morpho steps
            self.do_stan = self.read_param(yd, 'morpho.do_stan', 'required')
            self.do_postprocessing = self.read_param(yd, 'morpho.do_postprocessing', 'required')
            self.do_plots = self.read_param(yd, 'morpho.do_plots', 'required')
            self.wait = self.read_param(yd, 'morpho.wait_at_the_end', False)

            # Identifications
            self.job_id = self.read_param(yd, 'stan.job_id', '0')

            # STAN model stuff
            self.model_code = self.read_param(yd, 'stan.model.file', 'required')
            self.functions_code = self.read_param(yd, 'stan.model.function_file', None)
            self.model_name = self.read_param(yd, 'stan.model.model_name', None)
            self.cashe_dir = self.read_param(yd, 'stan.model.cache', './cache')

            # STAN data
            datafiles = self.read_param(yd, 'stan.data', None)
            if datafiles is not None:
                logger.debug("Loading datafiles")
                self.data = pyL.stan_data_files(datafiles)

            # STAN run conditions
            self.algorithm = self.read_param(yd, 'stan.run.algorithm', 'NUTS')
            self.iter = self.read_param(yd, 'stan.run.iter', 2000)
            self.warmup = self.read_param(yd, 'stan.run.warmup', self.iter/2)
            self.chains = self.read_param(yd, 'stan.run.chain', 4)
            # Adding a seed based on extra arguments, current time
            if isinstance(args.seed,int):
                self.seed=args.seed
            elif args.autoseed:
                self.seed = int(random.random()*1000000000) # seed based on random.random and the current system time
                logger.debug("Autoseed activated: seed = {}".format(self.seed))
            else:
                self.seed = self.read_param(yd, 'stan.run.seed', None)

            self.thin = self.read_param(yd, 'stan.run.thin', 1)
            self.init_per_chain = self.read_param(yd, 'stan.run.init', '')
            self.init = self.init_Stan_function();

            # plot and print information
            self.plot_vars = self.read_param(yd, 'stan.plot', None)

            # output information
            self.out_format = self.read_param(yd, 'stan.output.format', 'root')
            self.out_fname = self.read_param(yd, 'stan.output.name','stan_out.root')

            self.out_tree = self.read_param(yd, 'stan.output.tree', None)
            self.out_branches = self.read_param(yd, 'stan.output.branches', None)

            self.out_cfg = self.read_param(yd, 'stan.output.config', None)
            self.out_vars = self.read_param(yd, 'stan.output.data', None)

            # Outputted pickled fit filename
            self.out_fit = self.read_param(yd, 'stan.output.fit', None)

            # Outputted text file containing name of cache file
            self.out_cache_fn = self.read_param(yd, 'stan.output.save_cache_name', None)

            # Post-processing configuration
            self.pp_out_fname = self.read_param(yd, 'postprocessing.output.name', 'processed_stan_out.root')
            self.pp_out_format = self.read_param(yd, 'postprocessing.output.format', 'root')
            self.pp_dict = self.read_param(yd, 'postprocessing.which_pp', None)

            # Plot configuration
            self.plot_dict = self.read_param(yd, 'plot.which_plot', None)

        except Exception as err:
            raise err

def stan_cache(model_code, functions_code, model_name=None, cashe_dir='.',**kwargs):
    """Use just as you would `stan`"""

    theModel = open(model_code,'r+').read()
    match =  re.findall(r'\s*include\s*=\s*(?P<function_name>\w+)\s*;*',theModel)
    for matches in match:
        for key in functions_code:
            if (key['name']==matches):
                StanFunctions = open(key['file'],'r+').read()
                theModel = re.sub(r'\s*include\s*=\s*'+matches+'\s*;*\n',StanFunctions, theModel, flags=re.IGNORECASE)

    code_hash = md5(theModel.encode('ascii')).hexdigest()
    if model_name is None:
        cache_fn = '{}/cached-model-{}.pkl'.format(cashe_dir, code_hash)
    else:
        cache_fn = '{}/cached-{}-{}.pkl'.format(cashe_dir, model_name, code_hash)

    if (args.force_restart):
        logger.debug("Forced to create Stan cache!")
        sm = pystan.StanModel(model_code=theModel)
        with open(cache_fn, 'wb') as f:
            pickle.dump(sm, f)
    else:
        try:
            logger.debug("Trying to load cached StanModel")
            sm = pickle.load(open(cache_fn, 'rb'))
        except:
            logger.debug("Creating Stan cache!")
            sm = pystan.StanModel(model_code=theModel)
            with open(cache_fn, 'wb') as f:
                pickle.dump(sm, f)
        else:
            logger.debug("Using cached StanModel")

    if sa.out_cache_fn is not None:
        logger.debug("Saving cache file to {}".format(sa.out_cache_fn))
        cache_name_file = open(sa.out_cache_fn,'w+')
        cache_name_file.write(cache_fn)

    logger.info("Starting the sampling")
    return sm.sampling(**kwargs)

def parse_args():
    '''
    Parse the command line arguments provided to morpho.
    '''
    p = ArgumentParser(description='''
        An analysis tool for Project 8 data.
    ''')
    p.add_argument('-c','--config',
                   metavar='<configuration file>',
                   help='Full path to the configuration file used by morpho',
                   required=True)
    p.add_argument('--job_id',
                   metavar='<job_id>',
                   help='Job id number for batching',
                   required=False)
    p.add_argument('-s','--seed',
                   metavar='<seed>',
                   help='Add random seed number to file',
                   required=False)
    p.add_argument('-f','--force-restart',
                   action='store_true',
                   default=False,
                   help='Force the creation of a cache',
                   required=False)
    p.add_argument('-as','--autoseed',
                   action='store_true',
                   default=False,
                   help='Generate the seed based on the current time in ms',
                   required=False)
    return p.parse_args()


def open_or_create(hdf5obj, groupname):
    """
    Create a group within an hdf5 object if it doesn't already exist,
    and return the resulting group.
    """
    if groupname != "/" and groupname not in hdf5obj.keys():
        hdf5obj.create_group(groupname)
    return hdf5obj[groupname]

def plot_result(conf, stanres):
    """
    Plot variables as specified.
    """
    fit = stanres.extract()
    if conf.plot_vars is not None:
        for var in conf.plot_vars:
            parname = var['variable']
            if parname not in fit:
                warning = """WARNING: data {0} not found in fit!  Skipping...
                """.format(parname)
                logger.debug(warning)
            else:
                stanres.plot(parname)

def write_result(conf, stanres):
    logger.info("Writing results!")
    ofilename = sa.out_fname
    if (args.job_id>0):
        ofilename = ofilename+'_'+args.job_id
    if sa.out_format == 'hdf5':
        #ofilename = ofilename+'.h5'
        pyL.write_result_hdf5(sa, ofilename, stanres)

    if sa.out_format == 'root':
        ofilename = ofilename+'.root'
        pyL.stan_write_root(sa, ofilename, stanres)
    return stanres

def sampleFunc(arg):
    logger.info('you called sampleFunc({})'.format(arg))

def postprocessing(sa):
    # Generic function for creating the PostProcessing class
    for minidict in sa.pp_dict:
        logger.info("Doing postprocessing {}".format(minidict['method_name']))
        modulename = 'postprocessing.'+minidict['module_name']
        i = importlib.import_module("{}".format(modulename))
        try:
            getattr(i,minidict['method_name'])(minidict)
        except Exception as err:
            logger.debug(err)
    return 1

def plotting(sa):
    # Generic function for creating the PostProcessing class
    list_canvas = []
    for minidict in sa.plot_dict:
        logger.info("Doing plot {}".format(minidict['method_name']))
        modulename = 'plot.'+minidict['module_name']
        i = importlib.import_module("{}".format(modulename))
        try:
            list_canvas.append(getattr(i,minidict['method_name'])(minidict))
        except Exception as err:
            logger.debug(err)

    return list_canvas

def save_object(obj, filename):
    logger.info("Saving into pickle file: {}".format(filename))
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    logger.info("Welcome to morpho")
    args = parse_args()
    with open(args.config, 'r') as cfile:
        try:
            cdata = yload(cfile)
            sa = morpho(cdata)
            if (sa.get_do_Stan()):
                logger.info("Doing MC with Stan")
                result = stan_cache(**(sa.gen_arg_dict()))
                stanres = write_result(sa, result)
                if sa.out_fit != None:
                    save_object(stanres, sa.out_fit)
                    logger.debug('Saved fit in {}'.format(sa.out_fit))
            if (sa.get_do_pp()):
                postprocessing(sa)
            if (sa.get_do_plots()):
                list_canvas = plotting(sa)
            if(sa.get_wait()):
                raw_input('Press <ret> to end -> ')
        except Exception as err:
            logger.debug(err)
