# Definitions for loading and using pystan for analysis using root or hdf5

import logging
logger = logging.getLogger('pystanLoad')
logger.setLevel(logging.DEBUG)
base_format = '%(asctime)s[%(levelname)-8s] %(name)s(%(lineno)d) -> %(message)s'
logging.basicConfig(format=base_format, datefmt='%m/%d/%Y %H:%M:%S')

try:
    from ROOT import *
except ImportError:
    logger.debug("Cannot import ROOT")
    pass

try:
    import h5py
except ImportError:
    logger.debug("Cannot import h5py")
    pass

import pystan
import numpy as np
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

def theHack(theString,theVariable,theSecondVariable="",theThirdVariable=""):
    theResult = str(theString.format(theVariable,theSecondVariable,theThirdVariable))
    return theResult



# Reading dict data file (in R) and other input files (hdf5 or root).

def stan_data_files(theData):
    alist = {}
    for tags in theData.keys():
        for key in theData[tags]:
            if tags=='files':
                atype = key['format']
                afile = None

                if atype =='R' :
                    afile = pystan.misc.read_rdump(key['name'])
                    alist = dict(alist.items() + afile.items())
                    for key, value in alist.iteritems():
                        translist = value.tolist()
                        alist.update({key: translist})

                elif atype =='hdf5' :
                    afile = h5py.File(key['name'], 'r') #Reading from hdf5 file

                    areal = array.array('d',[0.])
                    aint  = array.array('i',[0])

                    for lbr in key['datasets']:
                        dataset = afile[lbr['nm']] or afile[lbr['nm']+"."]
                        if dataset:
                            nObjects = dataset.size #Datasets - typically arrays of generated quantities

                            #Naming and specifying data type
                            if 'stan_alias' in lbr.keys():
                                aname = str(lbr['stan_alias'])
                            else:
                                aname = str(lbr['nm'])

                            if 'data_format' in lbr.keys():
                                adataformat =  str(lbr['data_format'])
                            else:
                                adataformat = 'float'

                            for iEntry in range(nObjects):
                                if (adataformat=='float'):
                                    areal[0] = dataset[iEntry]
                                    insertIntoDataStruct(aname, areal[0], alist)

                                else:
                                    integer = int(dataset[iEntry]) #Converting to integer array
                                    aint[0] = integer
                                    insertIntoDataStruct(aname, aint[0], alist)

                elif atype =='root':
                    logger.debug('Getting {} in {}'.format(key['tree'],key['name']))
                    afile = TFile.Open(key['name'],'read')
                    atree = TTree()
                    afile.GetObject(str(key['tree']), atree)

                    aCut = readLabel(key,'cut',None)

                    if aCut is not None:
                        atree = atree.CopyTree(aCut)

                    nEvents = atree.GetEntries()
                    alist['nData'] = int(nEvents)

                    areal = array.array('d',[0.])
                    aint  = array.array('i',[0])

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

                        if 'data_format' in lbr.keys():
                            adataformat =  str(lbr['data_format'])
                        else:
                            adataformat = 'float'

                        branch.GetEntry(0)>0
                        for iEntry in range(nEvents):
                            atree.GetEntry(iEntry)

                            leaf = None
                            if leaf is None:
                                if (adataformat=='float'):
                                    areal[0] = getattr(atree, lbr['name'])
                                    insertIntoDataStruct(aname,areal[0], alist)

                                else:
                                    aint[0] = int(getattr(atree, lbr['name']))
                                    insertIntoDataStruct(aname,aint[0], alist)
                            else:
                                avalue = branch.GetValue(iEntry,1)
                                insertIntoDataStruct(aname, avalue, alist)
                        if len(alist[aname])==1:
                            alist.update({aname: alist[aname][0]})
                    afile.Close()

                else:
                    logger.warning('{} format not yet implemented.'.format(atype))
            elif tags=='parameters':
                alist = dict(alist.items() + key.items())

    return alist

def theTrick(thedict,uppertreename=""):

    newdict = {}
    for key,value in thedict.iteritems():
        if isinstance(value, dict):
            subdict = theTrick(value,uppertreename+key+".")
            newdict.update(subdict)
        else:
            newdict.update({uppertreename+key:value})
    return newdict


def write_result_hdf5(conf, ofilename, stanres, input_param):
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
                logger.debug(warning)
            else:
                g[var['output_name']] = fit[stan_parname]
    logger.info('The file has been written to {}'.format(ofilename))

# transform a dictionary into a tree

def build_tree_from_dict(treename,input_param):
    logger.debug("Creating tree '{}'".format(treename))
    atree = TTree(treename,treename)
    dictToFill = {}
    treeToAddFriend = {}
    for key,value in input_param.iteritems():
        if isinstance(value,int) or isinstance(value,float):
            nSize = 1
            if isinstance(value, float):
                nType = 'float'
                pType = '/D'
            elif isinstance(value, int):
                nType = 'int'
                pType = '/I'
            exec(theHack("theVariable_{} = np.zeros({}, dtype={})",str(key).replace(".","_"),nSize,nType))
            exec(theHack("atree.Branch(str(key), theVariable_{}, key+'{}')",str(key).replace(".","_"),pType))
        elif isinstance(value,str):
            nSize = 1
            stringLength = len(value)
            if stringLength<1:
                continue
            pType = '/C'
            exec(theHack("theVariable_{} = np.chararray({},itemsize={})",str(key).replace(".","_"),nSize,stringLength))
            exec(theHack("atree.Branch(str(key), theVariable_{}, key+'{}')",str(key).replace(".","_"),pType))

        elif isinstance(value,list):
            nSize = len(value)
            if isinstance(value[0], float):
                nType = 'float'
                pType = '/D'
            elif isinstance(value[0], int):
                nType = 'int'
                pType = '/I'
            else:
                continue
            exec(theHack("theVariable_{} = np.zeros({}, dtype={})",str(key).replace(".","_"),nSize,nType))
            exec(theHack("atree.Branch(str(key), theVariable_{}, key+'[{}]{}')",str(key).replace(".","_"),nSize,pType))

        dictToFill.update({key:value})

    # Filling the input param tree
    for key,value in dictToFill.iteritems():
        if isinstance(value,list):
            for iNum in range(0,len(value)):
                exec(theHack("theVariable_{}[{}] = value[{}]",str(key).replace(".","_"),iNum,iNum))
        else:
            exec(theHack("theVariable_{}[0] = value",str(key).replace(".","_")))
    atree.Fill()
    return atree

# save Stan input and output into a root file
def stan_write_root(conf, theFileName, theOutput, input_param):

    logger.debug("Creating ROOT file {}".format(theFileName+".root"))
    if conf.out_option:
        afile = TFile.Open(theFileName, conf.out_option)
    else:
        afile = TFile.Open(theFileName, "RECREATE")

    # save the input parameters
    logger.debug("saving Stan input parameters")
    newdict = theTrick(input_param)
    treeinputdata = build_tree_from_dict("stan_model_param",newdict)
    treeinputdata.Write()

    # save results
    logger.debug("saving Stan results")
    # theOutputVar = conf.out_branches
    # theOutputData = {}
    # for key in theOutputVar:
    #     theOutputData.update({key['root_alias']:theOutput.extract(key['variable'])[key['variable']].tolist()})
    # atree = build_tree_from_dict(conf.out_tree,theOutputData)
    # atree.Write()
    atree = TTree(conf.out_tree,conf.out_tree)
    theOutputVar = conf.out_branches
    theOutputData = {}

    nBranches = len(theOutputVar)
    iBranch = 0
    for key in theOutputVar:
        nSize = readLabel(key,'ndim',1)

        pType = '/D'
        nType = readLabel(key,'type','float')
        if (nType=='int') :
            pType='/I'

        exec(theHack("theVariable_{} = np.zeros({}, dtype={})",str(key['root_alias']),nSize,nType))

        if (nSize == 1) :
            exec(theHack("atree.Branch(str(key['root_alias']), theVariable_{}, key['root_alias']+'{}')",str(key['root_alias']),pType))
        else :
            exec(theHack("atree.Branch(str(key['root_alias']), theVariable_{}, key['root_alias']+'[{}]{}')",str(key['root_alias']),nSize,pType))

        theOutputData[iBranch] = theOutput.extract(key['variable'])
        nEvents = len(theOutputData[iBranch][key['variable']])
        iBranch += 1

    for iEvent in range(0,nEvents):
        iBranch = 0
        for key in theOutputVar:
            theValue = theOutputData[iBranch][key['variable']][iEvent]
            nSize = readLabel(key,'ndim',1)
            if (nSize == 1) :
                exec(theHack("theVariable_{}[0] = theValue",str(key['root_alias'])))
            else :
                for iNum in range(0,nSize):
                    exec(theHack("theVariable_{}[{}] = theValue[{}]",str(key['root_alias']),iNum,iNum))
            iBranch +=1
        atree.Fill()

    atree.Write()
    afile.Close()

    logger.info('The file has been written to {}'.format(theFileName))
