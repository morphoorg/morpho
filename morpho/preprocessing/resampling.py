'''
Implement some resampling methods
'''

import logging
logger = logging.getLogger(__name__)

import ROOT as root

def bootstrapping(param_dict):
    '''
    Resample the content of a tree usng a bootstrap technique (some samples can be used twice).
    '''

    logger.debug("Making bootstrapping")
    input_file_name = param_dict['input_file_name']
    input_tree = param_dict['input_tree']
    if 'output_tree' in param_dict:
        output_tree = param_dict['output_tree']
    else:
        output_tree = input_tree
    if 'output_file_name' in param_dict:
        output_file_name = param_dict['output_file_name']
    else:
        output_file_name = input_file_name
    number_interation = param_dict['number_data']
    if input_tree == output_tree and input_file_name == output_file_name:
        logger.critical("indentical input and output. filename: {}; tree: {}".format(input_file_name,input_tree))
        raise

    file = root.TFile(input_file_name,"READ")
    tree = file.Get(input_tree)
    nEntries = tree.GetEntries()
    logger.debug("Sampling {} points from {} in {}:{}".format(number_interation,nEntries,input_file_name,input_tree))
    newtree=tree.CloneTree(0)
    newtree.SetName(output_tree)
    root.gRandom.SetSeed()
    for i in range(number_interation):
        n = root.gRandom.Uniform()*nEntries
        tree.GetEntry(int(n))
        newtree.Fill()
    if input_file_name is not output_file_name:
        g=root.TFile(output_file_name,"RECREATE")
    else:
        g = root.TFile(input_file_name,"UPDATE")
    g.cd()
    newtree.Write()
    g.Close()
    file.Close()
    logger.debug("Resampling complete; results saved in {}:{}".format(output_file_name,output_tree))