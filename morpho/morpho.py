#!/usr/bin/env python

#
# morpho.py
#
# author: j.n. kofron <jared.kofron@gmail.com>
#
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import re
import pystan
import pystanLoad as pyL
import json
import fileinput

from pystan import stan
from h5py import File as HDF5
from yaml import load as yload
from argparse import ArgumentParser
from inspect import getargspec

import pickle
from hashlib import md5

class stan_args(object):
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
                print(err)
                raise exc
            else:
                data = default
        return data

    def gen_arg_dict(self):
        d = self.__dict__
        sca = getargspec(stan_cache)
        sa = getargspec(stan)
        return {k: d[k] for k in (sa.args + sca.args) if k in d}

    def init_function(self):
        return self.init_per_chain
    
    def __init__(self, yd):
        try:
            # Identifications
            self.job_id = self.read_param(yd, 'stan.job_id', '0')

            # STAN model stuff
            self.model_code = self.read_param(yd, 'stan.model.file', 'required')
            self.functions_code = self.read_param(yd, 'stan.model.function_file', None)
            self.cashe_dir = self.read_param(yd, 'stan.model.cache', './cache')

            # STAN data
            datafiles = self.read_param(yd, 'stan.data', 'required')
            self.data = pyL.stan_data_files(datafiles)

            # STAN run conditions
            self.algorithm = self.read_param(yd, 'stan.run.algorithm', 'NUTS')
            self.iter = self.read_param(yd, 'stan.run.iter', 2000)
            self.warmup = self.read_param(yd, 'stan.run.warmup', self.iter/2)
            self.chains = self.read_param(yd, 'stan.run.chain', 4)
            self.seed = self.read_param(yd, 'stan.run.seed', 314159)
            self.thin = self.read_param(yd, 'stan.run.thin', 1)
            self.init_per_chain = self.read_param(yd, 'stan.run.init', '')
            self.init = self.init_function();
                        
            # plot and print information
            self.plot_vars = self.read_param(yd, 'stan.plot', None)

            # output information
            self.out_format = self.read_param(yd, 'stan.output.format', 'hdf5')
            self.out_fname = self.read_param(yd, 'stan.output.name',
                                                 'stan_out.h5')

            self.out_tree = self.read_param(yd, 'stan.output.tree', None)
            self.out_branches = self.read_param(yd, 'stan.output.branches', None)

            self.out_cfg = self.read_param(yd, 'stan.output.config', None)
            self.out_vars = self.read_param(yd, 'stan.output.data', None)
            
            # Outputted pickled fit filename
            self.out_fit = self.read_param(yd, 'stan.output.fit', None)
            
        except Exception as err:
            raise err

def stan_cache(model_code, functions_code, model_name=None, cashe_dir='.',**kwargs):
    """Use just as you would `stan`"""

<<<<<<< HEAD:morpho/morpho.py
    theData = open(model_code,'r+').read()
    code_hash = md5(theData.encode('ascii')).hexdigest()
=======
    theModel = open(model_code,'r+').read()
    match =  re.findall(r'\s*include\s*<-\s*(?P<function_name>\w+)\s*;*',theModel)
    for matches in match:
        for key in functions_code:
            if (key['name']==matches):
                StanFunctions = open(key['file'],'r+').read()
                theModel = re.sub(r'\s*include\s*<-\s*'+matches+'\s*;*\n',StanFunctions, theModel, flags=re.IGNORECASE)
                
    code_hash = md5(theModel.encode('ascii')).hexdigest()
>>>>>>> develop:morpho/morpho.py
    if model_name is None:
        cache_fn = '{}/cached-model-{}.pkl'.format(cashe_dir, code_hash)
    else:
        cache_fn = '{}/cached-{}-{}.pkl'.format(cashe_dir, model_name, code_hash)
    try:
        sm = pickle.load(open(cache_fn, 'rb'))
    except:
<<<<<<< HEAD:morpho/morpho.py
        theModel = theData
        if functions_code:
            match = re.findall(r"(?<=include_functions<-)\w+",theData, flags=re.IGNORECASE)
            if match:
                for matches in match:
                    for key in functions_code:
                        if (key['name']==matches):
                            StanFunctions = open(key['file'],'r+').read()
                            theModel = re.sub("include_functions<-"+matches, StanFunctions, theModel, flags=re.IGNORECASE)
=======
>>>>>>> develop:morpho/morpho.py
        sm = pystan.StanModel(model_code=theModel)
        with open(cache_fn, 'wb') as f:
            pickle.dump(sm, f)
    else:
        print("Using cached StanModel")
    return sm.sampling(**kwargs)

def parse_args():
    '''
    Parse the command line arguments provided to morpho.
    '''
    p = ArgumentParser(description='''
        An analysis tool for Project 8 data.
    ''')
    p.add_argument('--config',
                   metavar='<configuration file>',
                   help='Full path to the configuration file used by morpho',
                   required=True)
    p.add_argument('--job_id',
                   metavar='<job_id>',
                   help='Job id number for batching',
                   required=False)
    p.add_argument('--seed',
                   metavar='<seed>',
                   help='Add random seed number to file',
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
                print warning
            else:
                stanres.plot(parname)
        print(result)

def write_result(conf, stanres):

    ofilename = sa.out_fname
    if (args.job_id>0):
        ofilename = ofilename+'_'+args.job_id        
    if sa.out_format == 'hdf5':
        #ofilename = ofilename+'.h5'
        write_result_hdf5(sa, ofilename, result)

    if sa.out_format == 'root':
        ofilename = ofilename+'.root'
        pyL.stan_write_root(sa, ofilename, result)
    return stanres

def write_result_hdf5(conf, ofilename, stanres):
    """
    Write the STAN result to an HDF5 file.
    """
    with HDF5(ofilename,'w') as ofile:
        g = open_or_create(ofile, conf.out_cfg['group'])
        fit = stanres.extract()
        for var in conf.out_vars:
            stan_parname = var['stan_parameter']
            if stan_parname not in fit:
                warning = """WARNING: data {0} not found in fit!  Skipping...
                """.format(stan_parname)
                print warning
            else:
                print(var['output_name'])
                g[var['output_name']] = fit[stan_parname]
                
def save_object(obj, filename):
    with open(filename, 'wb') as output:
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)

if __name__ == '__main__':
    args = parse_args()
    with open(args.config, 'r') as cfile:
        try:
            cdata = yload(cfile)
            sa = stan_args(cdata)

            result = stan_cache(**(sa.gen_arg_dict()))

            stanres = write_result(sa, result)
            plot_result(sa, result)
        
            save_object(stanres, sa.out_fit)
                                        
        except Exception as err:
            print(err)
