# Definitions for loading and using pystan for analysis using root or hdf5

# import logging
from morpho.utilities import morphologging
logger = morphologging.getLogger(__name__)

# import pystan
# import numpy as np

def extract_data_from_outputdata(conf,theOutput):
    # Extract the data into a dictionary
    # when permuted is False, the entire thing is returned (key['variable'] is ignored)
    logger.debug("Extracting samples from pyStan output")
    theOutputDiagnostics = theOutput.get_sampler_params(inc_warmup=True)

    diagnosticVariableName = ['accept_stat__','stepsize__','n_leapfrog__','treedepth__','divergent__','energy__']

    # if include warmupm we have to extract the entire data and parse it to get the
    # if conf.out_inc_warmup:
    theOutputData = theOutput.extract(permuted=False,inc_warmup=True)
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
    for key in conf['interestParams']:
        if key not in diagnosticVariableName:
            desired_var.append(key)

    for iChain in range(0,conf['chains']):
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
            theOutputDataDict["is_sample"].append(0 if iEvents< conf['warmup'] else 1)
    return theOutputDataDict
