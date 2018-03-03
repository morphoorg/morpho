'''
Run Stan repeatedly with the same config file and
chain together resulting ROOT files (inputs to Stan
may vary, if the sample_inputs preprocessor is used).
'''

import logging
logger = logging.getLogger(__name__)

import os
import ROOT as ROOT

def ensemble(param_dict):
    logger.info("Performing {} Stan runs.".format(param_dict['Nruns']))
    
    chain = TChain(param_dict['result_trees'][0])
    for i in range(param_dict('Nruns')):
        morpho -c param_dict['config_name']
        file_to_chain = _rename_files(param_dict, i)
        #if len(file_to_chain) == 1:
        #    chain.Add(param_dict['result_path'+file_to_chain[0]]
        #    for tree in param_dict['result_trees'][1:]:
        #        chain.Add('result_path'+file_to_chain[0]+'/'+tree)
        #else:
        #    logger.debug("Attempted to chain {} root files with the same identifiers. TChain not created.".format(len(file_to_chain)))


def _rename_files(param_dict, label):
    rpath = param_dict['result_path']
    root_names = []
    for filename in os.listdir(rpath):
        if param_dict['result_ID'] in filename and not filename[0].isdigit():
            os.rename(os.path.join(rpath, filename), os.path.join(rpath, str(label)+filename))
            if ".root" in filename:
                root_names.append(filename)
    return root_names


