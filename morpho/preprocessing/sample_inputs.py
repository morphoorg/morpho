'''
Select Stan "data" parameter inputs by sampling from priors.

Below is an example preprocessing configuration dictionary.

preprocessing:
  which_pp:
    - method_name: sample_inputs
      module_name: sample_inputs
      params_to_sample:
        - name: Q
          prior_dist: normal
          prior_params: [18575., 0.2]
        - name: sigma_value
          prior_dist: normal
          prior_params: [0.04, 0.004]
      fixed_params:
        - name: KEmin
          val: 18574.
        - name: KEmax
          val: 18575.4
        - name: background_fraction
          val: 0.05,
        - name: sigma_error
          val: 0.004
        - name: u_value
          val: 0
        - name: u_spread
          val: 70
        - name: mass
          val: 0.2 
      output_file_name: "./tritium_model/results/beta_spectrum_2-19_ensemble.root" 
      tree: inputs
'''


import logging
logger = logging.getLogger(__name__)

try:
    import ROOT as ROOT# import ROOT, TStyle, TCanvas, TH1F, TGraph, TLatex, TLegend, TFile, TTree, TGaxis, TRandom3, TNtuple, TTree
    import numpy as np
    import random
    from array import array
except ImportError:
    pass


def sample_inputs(param_dict):
    outfile = ROOT.TFile(param_dict['output_file_name'],"RECREATE")
    # Create a ROOT tree
    out_tree = ROOT.TTree(param_dict['tree'], param_dict['tree'])

    for sample_dict in param_dict['params_to_sample']:
        name = sample_dict['name']
        if sample_dict['prior_dist'] == 'normal':
            tmp_sampled_val = array('f',[ 0 ])
            b = out_tree.Branch(name, tmp_sampled_val, name+'/F')
            random.seed()
            rand = random.gauss(sample_dict['prior_params'][0], sample_dict['prior_params'][1])
            logger.info('Sampled value of {}: {}'.format(name, rand))
            tmp_sampled_val[0] = rand
            b.Fill()

        else:
            logger.debug('Sampling for {} distributions is not yet implemented'.format(sample_dict['prior_dist']))

    for fixed_dict in param_dict['fixed_params']:
        tmp_fixed_val = array('f',[ 0 ])
        b = out_tree.Branch(fixed_dict['name'], tmp_fixed_val, fixed_dict['name']+'/F')
        tmp_fixed_val[0] = fixed_dict['val']
        b.Fill()

    out_tree.Fill()
    outfile.Write()               
    outfile.Close()
    logger.info("Input parameters have been selected. Params in file: {}".format(param_dict['output_file_name']))
