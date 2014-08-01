# Definitions for loading and using pystan for analysis

import pystan

import numpy as np

import matplotlib
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt

import pickle
from hashlib import md5

from ROOT import TFile
from ROOT import TTree
from ROOT import TBranch

import array

# Inserting data into dict

def insertIntoDataStruct(name,aValue,aDict):
    if not name in aDict:
        aDict[name] = [aValue]
    else:
        aDict[name].append(aValue)

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

    for tags in theData.keys():
	for key in theData[tags]:
	    if tags=='files':
		atype = key['format']
		afile = None

		if atype =='R' :
		    afile = pystan.misc.read_rdump(key['name'])
		    alist = dict(alist.items() + afile.items())

		elif atype =='root' :		    

		    afile = TFile.Open(key['name'],'read')
		    atree = TTree()
		    afile.GetObject(str(key['tree']), atree)
		    
		    ar= array.array('d',[0])
		    nEvents = atree.GetEntries()
		    alist['nData'] = int(nEvents)
		    
		    for iEntry in range(0,nEvents):
			for lbr in key['branches']:
			    branch = atree.GetBranch(lbr['name'])
			    branch.SetAddress (ar)
			    atree.GetEntry(iEntry)
			    if 'stan_alias' in lbr.keys():
				aname = str(lbr['stan_alias'])
			    else:
				aname = str(lbr['name'])
			    insertIntoDataStruct(aname, ar[0], alist)
		else:
		    print atype,' format not implemented yet.'
	    elif tags=='parameters':
		alist = dict(alist.items() + key.items())

    return alist

