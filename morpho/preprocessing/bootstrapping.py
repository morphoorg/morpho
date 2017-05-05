'''
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

    file = root.TFile(input_file_name)
    tree = file.Get(input_tree)
    nEntries = tree.GetEntries()
    for i in range(number_interation):
        n = root.gRandom.Uniform()*nEntries
        print(int(n))
    print(tree.GetEntries())


    can = root.TCanvas("can","can",600,400)
    can.SaveAs('test.pdf')
