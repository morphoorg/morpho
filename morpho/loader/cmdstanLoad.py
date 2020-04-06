"""
Interfaces between filetypes used by CmdStan and root files.

Functions:
   - _extract_data_from_csv: Convert CmdStan csv output into a dictionary
"""

import logging
logger = logging.getLogger(__name__)

try:
    import ROOT
except ImportError:
    logger.debug("Cannot import ROOT")
    pass


def _extract_data_from_csv(conf,theOutput):
    """Extract the output data from a CmdStan csv into a dictionary

    Args:
        conf: morpho object, after Stan has been run
        theOutput: Csv file returned by CmdStan

    Returns:
        dictionary: Contains all extracted data
    """
    logger.debug("Extracting samples from CmdStan output")
    
    #Read all uncommented csv data into a dictionary
    dict_all_outputs = {}
    if conf.chains == 1:
        infiles = [conf.out_csv]
    else:
        infiles = [conf.out_csv.replace(".csv", str(i+1)+".csv") for i in range(conf.chains)]
    for file in infiles:
        with open(file) as csvfile:
            for line in csvfile:
                if line[0] != '#':
                    vars = line.strip('\n').split(",")
                    if len(dict_all_outputs) == 0:
                        varnames=vars
                        for key in varnames:
                            dict_all_outputs[key]=[]
                    else:
                        try:
                            float(vars[0])
                            for i in range(len(vars)):
                                dict_all_outputs[varnames[i]].append(float(vars[i]))
                        except:
                            pass #For all but the first file, skip the line listing variable names
                        
    #Create list of desired variables for root tree
    desired_data = []
    for key in conf.out_branches:
        if key['variable'] not in ['delta_energy__','lp_prob']:
            desired_data.append(key['variable'])
    if "lp__" not in desired_data:
        desired_data.append("lp__")
    if "divergent__" not in desired_data:
        desired_data.append("divergent__")
    logger.debug('Adding missing fields')
    desired_data.append("delta_energy__")

    #Create dictionary only containing outputs for desired variables
    theOutputDataDict = {}
    diagnosticVariableName = ['accept_stat__','stepsize__','n_leapfrog__','treedepth__','divergent__','energy__']
    for key in desired_data:
        if key in diagnosticVariableName:
                theOutputDataDict.update({str(key) : dict_all_outputs[key]})
        elif key == 'delta_energy__':
            list_value = dict_all_outputs['energy__']
            dE_list_value = []
            for i in range(len(list_value)):
                if i ==0:
                    dE_list_value.append(0)
                else:
                    dE_list_value.append(list_value[i]-list_value[i-1])
            theOutputDataDict.update({str(key) : dE_list_value})
        elif key == 'is_sample':
            logger.debug("Saving warmup runs is not supported for CmdStan, so variable 'is_sample' is not being created/saved.")
        else:
            for item in conf.out_branches:
                if item['variable'] == str(key):
                    if 'rescale' in item:
                        if type(item['rescale'][0])==str:
                            rescale = conf.data[item['rescale'][0]]
                        else:
                            rescale = item['rescale'][0]
                        operation = item['rescale'][1]
                        if operation=='add' or operation=='+':
                            post_list = [scaled+rescale for scaled in dict_all_outputs[key]]
                        elif operation=='subtract' or operation=='-':
                            post_list = [scaled-rescale for scaled in dict_all_outputs[key]]
                        elif operation=='multiply' or operation=='mult' or operation=='*':
                            post_list = [scaled*rescale for scaled in dict_all_outputs[key]]
                        elif operation=='divide' or operation=='div' or operation=='/':
                            post_list = [scaled/float(rescale) for scaled in dict_all_outputs[key]]
                        else:
                            logger.error("Rescaling operation {} is not an option. Not rescaling parameter.".format(operation))
                    else:
                        post_list = dict_all_outputs[key]
            theOutputDataDict.update({str(key) : post_list})

    return theOutputDataDict
