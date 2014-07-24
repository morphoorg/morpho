# Definitions for loading and using pystan for analysis

import pystan

import numpy as np

import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt

import pickle
from hashlib import md5

# make definition such that it is not necessary to recompile each and every time

def stan_cache(model_code, model_name=None, cashe_dir='.',**kwargs):
    """Use just as you would `stan`"""
    theData = open(model_code,'r+').read()
    code_hash = md5(theData.encode('ascii')).hexdigest()
    if model_name is None:
        cache_fn = '{}/cached-model-{}.pkl'.format(cashe_dir, code_hash)
    else:
        cache_fn = '{}/cached-{}-{}.pkl'.format(cashe_dir, model_name, code_hash)
    try:
        sm = pickle.load(open(cache_fn, 'rb'))
    except:
        sm = pystan.StanModel(file=model_code)
        with open(cache_fn, 'wb') as f:
            pickle.dump(sm, f)
    else:
        print("Using cached StanModel")
    return sm.sampling(**kwargs)

# reading dict file.  Right now it is set up as an R reader, but this can definitely be improved

def stan_data_files(theData):
    """Combine header and data files"""
    alist = {}
    for key in theData:
	afile = pystan.misc.read_rdump(theData[key])
	alist = dict(alist.items() + afile.items())
    return alist
