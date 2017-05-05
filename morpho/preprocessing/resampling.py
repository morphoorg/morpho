'''
Implement some resampling methods
'''

import logging
logger = logging.getLogger(__name__)

import ROOT as root


def bootstrapping(param_dict):
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

    logger.debug(input_file_name)
    file = root.TFile(input_file_name,"READ")
    tree = file.Get(input_tree)
    print(tree)
    nEntries = tree.GetEntries()
    logger.debug(nEntries)


    newtree=tree.CloneTree(0)
    for i in range(number_interation):
        n = root.gRandom.Uniform()*nEntries
        tree.GetEntry(int(n))
        newtree.Fill()
        logger.debug(int(n))
    logger.debug(tree.GetEntries())
    file.Close()
    if input_file_name is not output_file_name:
        g=root.TFile(output_file_name,"RECREATE")
    else:
        g = root.TFile(input_file_name,"UPDATE")
    g.cd()
    newtree.SetName(output_tree)
    newtree.Write()
    g.Close()
