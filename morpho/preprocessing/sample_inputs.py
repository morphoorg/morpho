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
          val: 0.05
        - name: sigma_error
          val: 0.004
        - name: u_value
          val: 0
        - name: u_spread
          val: 70
        - name: mass
          val: 0.2 
      transformed_inputs:
        - function: S
        - function: B
        - function: signal_frac
        - function: Ndata
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
    logger.info("Sampling inputs")
    outfile = ROOT.TFile(param_dict['output_file_name'],"RECREATE")
    # Create a ROOT tree
    out_tree = ROOT.TTree(param_dict['tree'], param_dict['tree'])
    inputs_dict = {}

    try:
        for sample_dict in param_dict['params_to_sample']:
            name = sample_dict['name']
            dist_error = 'Sampling for {} distribution is not yet implemented'.format(sample_dict['prior_dist'])
            tmp_sampled_val = array('f',[ 0 ])
            b = out_tree.Branch(name, tmp_sampled_val, name+'/F')

            random.seed()
            if 'strict_lower' in sample_dict:
                rand = sample_dict['strict_lower']-1
                while rand < sample_dict['strict_lower']:
                    rand = _draw_random_sample(sample_dict, dist_error)
            elif 'strict_upper' in sample_dict:
                try:
                    if rand > sample_dict['strict_upper']:
                        while rand < sample_dict['strict_lower'] or rand > sample_dict['strict_upper']:
                            rand = _draw_random_sample(sample_dict, dist_error)
                except:
                    rand = sample_dict['strict_upper']+1
                    while rand > sample_dict['strict_upper']:
                        rand = _draw_random_sample(sample_dict, dist_error)
            else:
                rand = _draw_random_sample(sample_dict, dist_error)

            logger.info('Sampled value of {}: {}'.format(name, rand))
            tmp_sampled_val[0] = rand
            inputs_dict[name] = rand
            b.Fill()
    except:
        pass

    try:
        for fixed_dict in param_dict['fixed_params']:
            name = fixed_dict["name"]
            if "type" in fixed_dict:
                if fixed_dict["type"]=="int" or fixed_dict["type"]=="integer":
                    tmp_fixed_val = array('i',[ 0 ])
                    b = out_tree.Branch(name, tmp_fixed_val, fixed_dict['name']+'/I')
                elif fixed_dict["type"]=="float":
                    tmp_fixed_val = array('f',[ 0 ])
                    b = out_tree.Branch(name, tmp_fixed_val, fixed_dict['name']+'/F')
                else:
                    logger.info('Type {} of parameter {} is not implemented.'.format(fixed_dict['type'], name))
            else:
                tmp_fixed_val = array('f',[ 0 ])
                b = out_tree.Branch(name, tmp_fixed_val, fixed_dict['name']+'/F')
            inputs_dict[name] = fixed_dict['val']
            tmp_fixed_val[0] = fixed_dict['val']
            b.Fill()
    except:
        pass

    try:
        for transformed_dict in param_dict['transformed_inputs']:
            func = transformed_dict['function']
            tmp_sampled_val = array('f',[ 0 ])
            b = out_tree.Branch(func, tmp_sampled_val, func+'/F')
            result = _compute_transformed_inputs(func, inputs_dict)
            tmp_sampled_val[0] = result
            inputs_dict[func] = result
            b.Fill()
            logger.info('Computed value of {}: {}'.format(func, result))
    except:
        pass

    out_tree.Fill()
    outfile.Write()               
    outfile.Close()
    logger.info("Input parameters have been selected. Params in file: {}".format(param_dict['output_file_name']))


def _draw_random_sample(sample_dict, dist_error):
    if sample_dict['prior_dist'] == 'normal':
        rand = random.gauss(sample_dict['prior_params'][0], sample_dict['prior_params'][1])
    elif sample_dict['prior_dist'] == 'lognormal':
        rand = np.random.lognormal(sample_dict['prior_params'][0], sample_dict['prior_params'][1], 1)[0]
    elif sample_dict['prior_dist'] == 'beta':
        rand = np.random.beta(sample_dict['prior_params'][0], sample_dict['prior_params'][1], 1)[0]
    elif sample_dict['prior_dist'] == 'gamma':
        rand = np.random.gamma(sample_dict['prior_params'][0], sample_dict['prior_params'][1], 1)[0]
    else:
        logger.debug(dist_error)
        return None
    return rand


def _compute_transformed_inputs(func, inputs_dict):
    func_error = 'The {} function is not yet implemented in sample_inputs'.format(func)
    Q = inputs_dict['Q']
    KEmin = inputs_dict['KEmin']
    KEmax = inputs_dict['KEmax']
    mass = inputs_dict['mass']
    t = inputs_dict['runtime']
    if func == 'S':
        A_s = inputs_dict['A_s']
        b = Q-KEmin
        N = 6./(mass**3-3.*mass**2*b+2.*b**3)
        #return t*N*A_s
        return t*A_s*b/1000.
    elif func == 'B':
        A_b = inputs_dict['A_b'] 
        return t*(KEmax - KEmin)*A_b
    elif func == 'signal_frac':
        return inputs_dict['S']/(inputs_dict['S']+inputs_dict['B'])
    elif func == 'Ndata':
        #This is a (hopefully temporary) hack.
        Ndata = 1
        while Ndata % 4 != 0:
            Ndata = np.random.poisson(inputs_dict['S']+inputs_dict['B'])
        return Ndata 
    else:
        logger.debug(func_error)
        return None

