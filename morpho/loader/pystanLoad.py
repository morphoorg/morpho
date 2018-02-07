"""
Import root and hdf5 files for use by pystan

Functions:
  - readLabel: Get an item from a dictionary
  - insertIntoDataStruct: Insert item into dictionary
  - theHack: Format a string
  - stan_data_files: Read in a dictionary of data files
  - extract_data_from_output_data: Extract Stan output into a dictionary
  - open_or_create: Create a group in an hdf5 object
  - write_result_hdf5: Write Stan results to an hdf5 file
  - theTrick: Transform dict into a dict with depth indicated by "."
  - transform\_list\_of\_dict\_into_dict:  Transform elements of any lists
    inside a dict into separate dict entries
  - build_tree_from_dict: Create a root TTree object from a dictionary
  - stan_write_root: Save Stan inputs and outputs into a root file
"""

import logging
logger = logging.getLogger(__name__)

try:
    import ROOT
except ImportError:
    logger.debug("Cannot import ROOT")
    pass

try:
    import h5py
except ImportError:
    logger.debug("Cannot import h5py")
    pass
try:
    import pystan
    import numpy as np
except ImportError:
    pass
import array
import bisect

def readLabel(aDict, name, default=None):
    """Get an item from a dictionary, or return default

    Args:
        aDict: Dictionary to search
        name: Key used to search aDict
        default: Default value returned if the given key does not exist.
            Defaults to None.

    Returns:
        aDict[name], or default if name does not exist
    """
    if not name in aDict:
        return default
    else :
        return aDict[name]

def insertIntoDataStruct(name,aValue,aDict):
    """Insert an item into a dictionary

    Args:
        name: Key used to insert item
        aValue: Value to insert
        aDict: Dictionary value is inserted into
    
    Returns:
        aDict with aValue inserted at name
    """
    if not name in aDict:
        aDict[name] = [aValue]
    else:
        aDict[name].append(aValue)

# execute the command of several combined strings
def theHack(theString,theVariable,theSecondVariable="",theThirdVariable=""):
    """Format theString using the given variables
    """
    theResult = str(theString.format(theVariable,theSecondVariable,theThirdVariable))
    return theResult

# Reading dict data file (in R) and other input files (hdf5 or root).
def stan_data_files(theData):
    """Read in a dictionary of R, hdf5 and root files

    theData must be a dictionary containing information about the
    data that should be read in for use by stan. theData should
    contain up to two dictionaries, stored with the keys 'files'
    and 'parameters'. These dictionaries should be set up as
    follows:

    Args:
      - theData.files.name: Name of the file to access
      - theData.files.format: Filetype. Options are 'R', 'root' or 'hdf5'
      - theData.files.datasets: List of datasets to be used when accessing\
      an hdf5 file (required only if 'format'=='hdf5')
      - theData.files.tree: Name of tree to access when accessing a root file\
    (required only if 'format'=='root')
      - theData.files.branches: Branches to be accessed in the given root tree
                (required only if 'format'=='root')
      - theData.files.cut: String specifying the cut for a root file (optional)
      - theData.parameters: All values from this list are added to\
            the returned list

    Returns:
        dictionary: All values from the given files are returned as a
        dictionary
    """
    alist = {}
    for tags in theData.keys():
        for key in theData[tags]:
            if tags=='files':
                atype = key['format']
                afile = None

                if atype =='R' :
                    logger.debug('Getting {}'.format(key['name']))
                    afile = pystan.misc.read_rdump(key['name'])
                    _save_repeated_as_arr(key['name'], afile)
                    for key_r, value in afile.items():
                        if(hasattr(value,"tolist")):
                            translist = value.tolist()
                            afile.update({key_r: translist})
                    alist.update(afile.items())
                    logger.debug('File {} added to data'.format(key['name']))
                elif atype =='hdf5' :
                    logger.debug('Getting {}'.format(key['name']))
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
                    logger.debug('File {} added to data'.format(key['name']))

                elif atype =='root':
                    logger.debug('Getting {} in {}'.format(key['tree'],key['name']))
                    afile = ROOT.TFile.Open(key['name'],'read')
                    atree = ROOT.TTree()
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
                    logger.debug('File {} added to data'.format(key['name']))

                else:
                    logger.warning('{} format not yet implemented.'.format(atype))
            elif tags=='parameters':
                logger.debug('Adding parameters from config file to data')
                alist.update(key)

    return alist

def _save_repeated_as_arr(rdump_filename, data_dict=dict()):
    """Save repeated elements in an rdump file as an array

    If a variable name is repeated in an rdump file, pystan.misc.read_rdump
    saves the last value of the variable and discards the rest. This method
    finds all variable names that are repeated, and for each name, it saves the
    corresponding data in a 2d array (for array inputs) or a 1d array (for scalar
    inputs). For example:
      x <- c(1,2)
      x <- c(3,4)
      x <- c(5,6)
    will result in a dictionary element {'x': numpy.array([[1,2],[3,4],[5,6]])}. Similarly,
      y <- 1
      y <- 2
      y <- 3
    will result in a dictionary element {'y' = numpy.array([1,2,3])}. Note that lines
    containing any other r data structures will be ignored.
    
    Args:
      rdump_filename- rdump formatted file
      data_dict- dictionary that will be modified to include repeated variables

    Returns:
      Returns data_dict, modified to include the arrays corresponding to each
      repeated variable
    """
    var_names = []
    var_data = []
    var_flatten = [] # Will be true if all inputs are a single value
    for line in open(rdump_filename, 'r'):
        splitline = map(str.strip,line.split("<-"))
        a= (list(splitline))
        if(len(list(splitline))<2):
            continue
        name = splitline[0]
        data = splitline[1]
        if(len(name)==0 or len(data)==0):
            continue
        # Ignore data that is not a 1d array or numeric
        if(('0'<=data[0] and data[0]<='9') or data[0]=='.'
           or data[0]=='c'):
            if(data[0]=='c'):
                data = list(map(float,data[2:-1].split(',')))
                arr_data = True
            elif('.' in data):
                data = [float(data)]
                arr_data = False
            else:
                data = [int(data)]
                arr_data = False

            idx = bisect.bisect_left(var_names, name)
            if(idx<len(var_names) and var_names[idx]==name):
                # This is a duplicate
                if(len(data)!=len(var_data[idx][-1])):
                    logger.warn('Array %s in file %s is jagged. PyStan cannot handle jagged arrays.'
                                % (name, rdump_filename))
                var_data[idx].append(data)
                var_flatten[idx] = var_flatten[idx] or not arr_data
            else:
                # This is the first ofccurence of this variable
                var_names.insert(idx, name)
                var_data.insert(idx, [data])
                var_flatten.insert(idx, not arr_data)
    for i in range(0,len(var_names)):
        if(len(var_data[i])>1):
            # This variable was duplicated at least once
            var_data[i] = np.array(var_data[i])
            if(var_flatten[i]):
                var_data[i] = np.ndarray.flatten(var_data[i])
            data_dict.update({var_names[i]: var_data[i]})
    return data_dict

def extract_data_from_outputdata(conf,theOutput):
    """Extract the output data from a morpho object into a dictionary

    Args:
        conf: morpho object, after Stan has been run
        theOutput: stanfit object returned by Stan

    Returns:
        dictionary: Contains all extracted data
    """
    # Extract the data into a dictionary
    # when permuted is False, the entire thing is returned (key['variable'] is ignored)
    logger.debug("Extracting samples from pyStan output")
    theOutputDiagnostics = theOutput.get_sampler_params(inc_warmup=conf.out_inc_warmup)

    diagnosticVariableName = ['accept_stat__','stepsize__','n_leapfrog__','treedepth__','divergent__','energy__']

    # if include warmupm we have to extract the entire data and parse it to get the
    if conf.out_inc_warmup:
        theOutputData = theOutput.extract(permuted=False,inc_warmup=conf.out_inc_warmup)
        logger.debug("Transformation into a dict")
        nEventsPerChain = len(theOutputData)
        # get the variables in the Stan4Model
        flatnames = theOutput.flatnames
        # add the diagnostic variable names
        flatnames.extend(diagnosticVariableName)

        # Clustering the data together
        theOutputDataDict = {}
        for key in flatnames:
            theOutputDataDict.update({str(key):[]})
        theOutputDataDict.update({"lp_prob":[]})
        theOutputDataDict.update({"delta_energy__":[]})
        theOutputDataDict.update({"is_sample":[]})

        # make list of desired variables
        desired_var = []
        for key in conf.out_branches:
            if key['variable'] not in diagnosticVariableName:
                desired_var.append(key['variable'])

        for iChain in range(0,conf.chains):
            for iEvents in range(0,nEventsPerChain):
                for iKey,key in enumerate(flatnames):
                    if key in diagnosticVariableName:
                        theOutputDataDict[str(key)].append(theOutputDiagnostics[iChain][key][iEvents])
                    else:
                        if key in desired_var:
                            theOutputDataDict[str(key)].append(theOutputData[iEvents][iChain][iKey])
                if iEvents is not 0:
                    theOutputDataDict["delta_energy__"].append(theOutputDiagnostics[iChain]['energy__'][iEvents]-theOutputDiagnostics[iChain]['energy__'][iEvents-1])
                else:
                    theOutputDataDict["delta_energy__"].append(0)
                theOutputDataDict["lp_prob"].append(theOutputData[iEvents][iChain][len(theOutput.flatnames)])
                theOutputDataDict["is_sample"].append(0 if iEvents< conf.warmup else 1)

    else:
        # make list of desired variables
        theOutputDataDict = {}
        desired_data = []
        for key in conf.out_branches:
            if key['variable'] not in diagnosticVariableName and key['variable'] not in ['delta_energy__','is_sample','lp_prob']:
                desired_data.append(key['variable'])
        if "lp__" not in desired_data:
            desired_data.append("lp__")
        theOutputData = theOutput.extract(pars=desired_data,permuted=True)
        logger.debug('Adding missing field')
        desired_data.append("is_sample")
        desired_data.append("delta_energy__")

        logger.debug('Transformation into a dict')
        desired_data.extend(diagnosticVariableName)
        for key in desired_data:
            if key in diagnosticVariableName:
                list_value = []
                for item in theOutputDiagnostics:
                    list_value.extend(item[str(key)].tolist())
                theOutputDataDict.update({str(key) : list_value})
            elif key == 'lp__':
                theOutputDataDict.update({'lp__':theOutputData[str('lp__')].tolist()})
                theOutputDataDict.update({'lp_prob':theOutputData[str('lp__')].tolist()})
            elif key == 'delta_energy__':
                list_value = []
                dE_list_value = []
                for item in theOutputDiagnostics:
                    list_value.extend(item['energy__'].tolist())
                for i, value in enumerate(list_value):
                    if i ==0:
                        dE_list_value.append(0)
                    else:
                        dE_list_value.append(list_value[i]-list_value[i-1])
                theOutputDataDict.update({str(key) : dE_list_value})
            elif key == 'is_sample':
                list_is_sample = [1]*len(theOutputData[str('lp__')])
                theOutputDataDict.update({'is_sample':list_is_sample})
            else:
                obj=theOutputData[str(key)]
                if isinstance(obj[0],np.ndarray):
                    list_obj = obj.tolist()
                    result = map(list, zip(*list_obj))
                    for i in range(0,len(result)):
                        theOutputDataDict.update({'{}[{}]'.format(str(key),i) : result[i]})
                else:
                    theOutputDataDict.update({str(key) : obj.tolist()})
    return theOutputDataDict

def open_or_create(hdf5obj, groupname):
    """ Return a group from an hdf5 object

    Args:
        hdf5obj: hdf5 object to access
        groupname: group to access or create

    Return:
        h5py.Group: Creates a group within the given hdf5 object if it
        doesn't already exist, then returns the group.
    """
    if groupname != "/" and groupname not in hdf5obj.keys():
        hdf5obj.create_group(groupname)
    return hdf5obj[groupname]

def write_result_hdf5(conf, theFileName, stanres, input_param):
    """Write the Stan result to an HDF5 file

    Args:
        conf: morpho object
        theFileName: Name of hdf5 output file, without the .h5 extension
        stanres: stanfit object containing the results to write
        input_param: No longer used

    Returns:
        None
    """
    try:
        import h5py
    except ImportError:
        logger.debug("Cannot import h5py")
        raise Exception
    theOutputDataDict = extract_data_from_outputdata(conf,stanres)
    with h5py.File(theFileName+'.h5','w') as ofile:
        g = open_or_create(ofile, conf.out_tree)
        for key in conf.out_branches:
            stan_parname = key['variable']
            nSize = readLabel(key,'ndim',1)
            if nSize==1:
                if stan_parname not in theOutputDataDict:
                    logger.warning("data {} not found".format(stan_parname))
                else:
                    g[key['hdf5_alias']] = theOutputDataDict[stan_parname]
            else:
                vector = []
                for iDim in range(0,nSize):
                    component_name = "{}[{}]".format(key[stan_parname],iDim)
                    if component_name not in theOutputDataDict:
                        logger.warning("data {} not found".format(stan_parname))
                        continue
                    else:
                        vector.append(theOutputDataDict[component_name])
                g[key['hdf5_alias']] = vector
    logger.info('The file has been written to {}'.format(theFileName+'.h5'))

# transform dict into items where the depth is indicated with "."
def theTrick(thedict,uppertreename=""):
    """Transform a dictionary of dictionaries into a depth 1 dictionary

    Takes a dictionary that contains other dictionaries and transforms it
    into a dictionary that has depth 1. The key for each value in the
    returned dictionary is that values path in the previous dictionary,
    with '.' indicating descent into a lower dictionary.

    Args:
        thedict: Dictionary to transform
        uppertreename: Prefix for all keys in the returned dictionary
    
    Returns:
        dictionary: Depth one dictionary containing the same values,
            with key names equal to the path through thedict
    """
    newdict = {}
    for key,value in thedict.items():
        if isinstance(value, dict):
            subdict = theTrick(value,uppertreename+key+".")
            newdict.update(subdict)
        else:
            newdict.update({uppertreename+key:value})
    return newdict

def transform_list_of_dict_into_dict(thedict):
    ''' Transform elements of lists into separate dict entries

    First, look for any list of dicts inside the dict and transform it
    into lists. Then, flatten any list of list into new list. For
    example, {'xxx':[[1,2],[2,3]]} transforms into
    {'xxx_1':[1,2],'xxx_2':[2,3]}) 

    Args:
        thedict: Dictionary to transform

    Returns:
       dictionary: the dict, with any elements that are lists separated
           into separate dictionary entries
    '''

    result_dict = {}
    for key,item in thedict.items():
        if isinstance(item,list):
            if isinstance(item[0],dict):
                newdict={}
                for k,v in [(subkey,d[subkey]) for d in item for subkey in d]:
                    if k not in newdict: newdict[k]=[v]
                    else: newdict[k].append(v)
                # flatten the dictionary
                flattened_dict = {}
                for subkey,subitem in newdict.items():
                    if isinstance(subitem[0],list):
                        for i in range(len(subitem[0])):
                            flattened_dict.update({'{}_{}'.format(subkey,i):[]})
                        for sublist in subitem:
                            for i,value in enumerate(sublist):
                                newlist = flattened_dict['{}_{}'.format(subkey,i)]
                                newlist.append(value)
                                flattened_dict.update({'{}_{}'.format(subkey,i):newlist})
                    else:
                        flattened_dict.update({subkey:subitem})
                result_dict.update({key:flattened_dict})
            else:
                result_dict.update({key:item})
        else:
            result_dict.update({key:item})
    return result_dict

def build_tree_from_dict(treename,input_param):
    """Create a root TTree object from a dictionary
    
    Args:
        treename: Desired name of the output tree
        input_param: Dictionary of values to place in tree. It must be
            depth 1.

    Returns:
        ROOT.TTree: Tree containing data from input_param
    """
    logger.debug("Creating tree '{}'".format(treename))
    atree = ROOT.TTree(treename,treename)
    dictToFill = {}
    treeToAddFriend = {}
    for key,value in input_param.items():
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
            dictToFill.update({key:value})
            continue
        elif isinstance(value,str):
            nSize = 1
            stringLength = len(value)
            if stringLength<1:
                continue
            pType = '/C'
            exec(theHack("theVariable_{} = np.chararray({},itemsize={})",str(key).replace(".","_"),nSize,stringLength))
            exec(theHack("atree.Branch(str(key), theVariable_{}, key+'{}')",str(key).replace(".","_"),pType))
            dictToFill.update({key:value})
            continue

        elif isinstance(value,list):
            nSize = len(value)
            if isinstance(value[0], float):
                nType = 'float'
                pType = '/D'
                exec(theHack("theVariable_{} = np.zeros({}, dtype={})",str(key).replace(".","_"),nSize,nType))
                exec(theHack("atree.Branch(str(key), theVariable_{}, key+'[{}]{}')",str(key).replace(".","_"),nSize,pType))
                dictToFill.update({key:value})
                continue
            elif isinstance(value[0], int):
                nType = 'int'
                pType = '/I'
                exec(theHack("theVariable_{} = np.zeros({}, dtype={})",str(key).replace(".","_"),nSize,nType))
                exec(theHack("atree.Branch(str(key), theVariable_{}, key+'[{}]{}')",str(key).replace(".","_"),nSize,pType))
                dictToFill.update({key:value})
                continue
            else:
                continue
    # Filling the input param tree
    for key,value in dictToFill.items():
        if isinstance(value,list):
            for iNum in range(0,len(value)):
                exec(theHack("theVariable_{}[{}] = value[{}]",str(key).replace(".","_"),iNum,iNum))
        else:
            exec(theHack("theVariable_{}[0] = value",str(key).replace(".","_")))
    atree.Fill()
    return atree

# save Stan input and output into a root file
def stan_write_root(conf, theFileName, theOutput, input_param):
    """Save Stan inputs and outputs ina  root files
    
    Args:
        conf: morpho object containing the configuration
        theFileName: Desired name of the output root file
        theOutput: stanfit object
        input_param: Dictionary containing any other parameters to be
            saved to the root tree

    Returns:
        None: The given theOutput and input_param values are saved to a
            root file named theFileName.
    """
    logger.debug("Creating ROOT file {}".format(theFileName))
    if conf.out_option:
        afile = ROOT.TFile.Open(theFileName, conf.out_option)
    else:
        afile = ROOT.TFile.Open(theFileName, "RECREATE")

    # save the input parameters
    logger.debug("Saving Stan input parameters")
    newdict = theTrick(input_param)
    flatdict = transform_list_of_dict_into_dict(newdict)
    newflatdict = theTrick(flatdict)
    treeinputdata = build_tree_from_dict("stan_model_param",newflatdict)
    treeinputdata.Write()

    # save results
    logger.debug("Saving Stan results")
    logger.debug("Creating tree '{}'".format(conf.out_tree))
    atree = ROOT.TTree(conf.out_tree,conf.out_tree)
    theOutputVar = conf.out_branches

    # Extract the data into a dictionary
    # when permuted is False, the entire thing is returned (key['variable'] is ignored)
    theOutputDataDict = extract_data_from_outputdata(conf,theOutput)

    logger.debug("Filling tree")
    # Create branches for any variable of interest
    nBranches = len(theOutputVar)
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

    # add an extra branch for warmup or sampling status
    thevariable_is_sample = np.zeros(1,dtype=int)
    atree.Branch("is_sample", thevariable_is_sample, "thevariable_is_sample/I")

    # add the data to the tree
    nEvents = len(theOutputDataDict['lp_prob'])
    nSample = 0
    nWarmup = 0
    for iEvent in range(0,nEvents):
        for key in theOutputVar:
            nSize = readLabel(key,'ndim',1)
            if (nSize == 1) :
                stanVariable = key['variable']

                theValue = theOutputDataDict[stanVariable][iEvent]
                exec(theHack("theVariable_{}[0] = theValue",str(key['root_alias'])))
            else :
                for iNum in range(0,nSize):
                    stanVariable = "{}[{}]".format(key['variable'],iNum)
                    theValue = theOutputDataDict[stanVariable][iEvent]
                    exec(theHack("theVariable_{}[{}] = theValue",str(key['root_alias']),iNum))
        thevariable_is_sample[0] = int(theOutputDataDict['is_sample'][iEvent])

        atree.Fill()

    atree.Write()
    afile.Close()
    logger.info('The file has been written to {}'.format(theFileName))
