# Definitions for loading and using pystan for analysis

from ROOT import *

import pystan

import pickle
from hashlib import md5

import array

def readLabel(aDict, name, default=None):
    if not name in aDict:
	return default
    else :
	return aDict[name]

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
		    
		    aCut = readLabel(key,'cut',None)

		    if aCut is not None:
			atree = atree.CopyTree(aCut)

		    nEvents = atree.GetEntries()
		    alist['nData'] = int(nEvents)

		    ar = array.array('d',[0.])
		    for lbr in key['branches']:
			branch = atree.GetBranch(lbr['name']) or atree.GetBranch(lbr['name']+".")
			if branch:
			    leaf= branch.GetLeaf(lbr['name'])
			    if not leaf:
				leaves= branch.GetListOfLeaves()
				if leaves and len(leaves)==1: leaf= leaves[0]
				else:                         leaf= None
			else:
			    leaf= atree.GetLeaf(lbr['name'])
			    branch= leaf.GetBranch()

			if 'stan_alias' in lbr.keys():
			    aname = str(lbr['stan_alias'])
			else:
			    aname = str(lbr['name'])

			branch.GetEntry(0)>0
			for iEntry in range(nEvents):
			    atree.GetEntry(iEntry)
			    if leaf is None:
				ar[0] = getattr(atree, lbr['name'])
				insertIntoDataStruct(aname,ar[0], alist)
			    else :
				avalue = branch.GetValue(iEntry,1)
				insertIntoDataStruct(aname, avalue, alist)

		    afile.Close()

		else:
		    print atype,' format not yet implemented.'
	    elif tags=='parameters':
		alist = dict(alist.items() + key.items())

    return alist

