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
import ROOT as ROOT# import ROOT, TStyle, TCanvas, TH1F, TGraph, TLatex, TLegend, TFile, TTree, TGaxis, TRandom3, TNtuple, TTree
import numpy as np
import random
from array import array
import math
import sys
from scipy.signal import convolve
from scipy.interpolate import interp1d

sys.path.insert(1, '/home/tweiss/scripts/Phase-II-official-analysis/fake-data-study')
import generate_tritium_spectrum as PhaseIIgen
logger.info("Script for generating Phase II data has been imported")

def sample_inputs(param_dict):
    logger.info("Sampling inputs")
    outfile = ROOT.TFile(param_dict['output_file_name'],"RECREATE")
    # Create a ROOT tree
    out_tree = ROOT.TTree(param_dict['tree'], param_dict['tree'])
    if 'array_tree' in param_dict:
        array_tree = ROOT.TTree(param_dict['array_tree'], param_dict['array_tree'])
    if 'dict_tree' in param_dict:
        dict_tree = ROOT.TTree(param_dict['dict_tree'], param_dict['dict_tree'])
    inputs_dict = {}

    try:
        for sample_dict in param_dict['params_to_sample']:
            name = sample_dict['name']
            dist_error = 'Sampling for {} distribution is not yet implemented'.format(sample_dict['prior_dist'])
            for i in range(len(sample_dict['prior_params'])):
                x = sample_dict['prior_params'][i]
                if type(x)==str:
                    sample_dict['prior_params'][i]=inputs_dict[x]

            random.seed()
            if 'strict_lower' in sample_dict:
                rand = sample_dict['strict_lower']-1.
                while rand < sample_dict['strict_lower']:
                    rand = _draw_random_sample(sample_dict, dist_error)
            elif 'strict_upper' in sample_dict:
                try:
                    if rand > sample_dict['strict_upper']:
                        while rand < sample_dict['strict_lower'] or rand > sample_dict['strict_upper']:
                            rand = _draw_random_sample(sample_dict, dist_error)
                except:
                    rand = sample_dict['strict_upper']+1.
                    while rand > sample_dict['strict_upper']:
                        rand = _draw_random_sample(sample_dict, dist_error)
            else:
                rand = _draw_random_sample(sample_dict, dist_error)

            logger.info('Sampled value of {}: {}'.format(name, rand))
            tmp_sampled_val = array('d',[rand])
            b = out_tree.Branch(name, tmp_sampled_val, name+'/D')
            inputs_dict[name] = rand
            b.Fill()
    except BaseException as error:
        logger.debug(error)
        pass

    try:
        for fixed_dict in param_dict['fixed_params']:
            name = fixed_dict["name"]
            if "type" in fixed_dict:
                if fixed_dict["type"]=="int" or fixed_dict["type"]=="integer":
                    tmp_fixed_val = array('i',[ 0 ])
                    b = out_tree.Branch(name, tmp_fixed_val, fixed_dict['name']+'/I')
                elif fixed_dict["type"]=="float" or fixed_dict["type"]=="double":
                    tmp_fixed_val = array('d',[ 0 ])
                    b = out_tree.Branch(name, tmp_fixed_val, fixed_dict['name']+'/D')
                else:
                    logger.info('Type {} of parameter {} is not implemented.'.format(fixed_dict['type'], name))
            else:
                tmp_fixed_val = array('d',[ 0 ])
                b = out_tree.Branch(name, tmp_fixed_val, fixed_dict['name']+'/D')
            inputs_dict[name] = fixed_dict['val']
            tmp_fixed_val[0] = fixed_dict['val']
            b.Fill()
    except BaseException as error:
        logger.debug(error)
        pass

    try:
        results = []
        names = []
        for transformed_dict in param_dict['transformed_inputs']:
            func = transformed_dict['function']
            if 'name' in transformed_dict:
                name = transformed_dict['name']
            else:
                name = func
            if 'unitchange' in transformed_dict:
                unitchange = transformed_dict['unitchange']
            else:
                unitchange = True
            result = _compute_transformed_inputs(func, inputs_dict, unitchange, transformed_dict)
            if isinstance(result, dict):
                for key, val in result.items():
                    inputs_dict[key]=val
                    #result = {name:result}
            else:
                inputs_dict[name] = result
            result = {name:result}
            for key, val in result.items():
                if isinstance(val, list):
                    results.insert(0,val)
                    names.insert(0,key)
                    logger.info('Values in array {} were computed.'.format(key))
                elif isinstance(val,dict):
                    results.insert(0, val)
                    names.insert(0, key)
                    for key1, val1 in val.items():
                        logger.info('Values in array {} were computed.'.format(key1))
                else:
                    results.append(val)
                    names.append(key)
                    logger.info('Computed value of {}: {}'.format(func, val))
    except BaseException as error:
        logger.debug(error)
        pass

    #treeList = ROOT.TList()
    for i in range(len(results)):
        if isinstance(results[i], list):
            tmp_val = array('d', [0]*len(results[i]))
            array_b = array_tree.Branch(names[i], tmp_val, names[i]+'['+str(len(results[i]))+']'+'/D')
            for j in range(len(results[i])):
                tmp_val[j] = results[i][j]
                array_tree.Fill()
        elif isinstance(results[i], dict):
            branch_names=[]
            if 'N' in results[i]:
                tmp_valA = array('i', [0]*len(results[i]['N']))
                arrayA = dict_tree.Branch('N', tmp_valA, 'N['+str(len(results[i]['N']))+']'+'/I')
                branch_names.append('N')
            if 'KE' in results[i]:
                tmp_valB = array('d', [0]*len(results[i]['KE']))
                arrayB = dict_tree.Branch('KE', tmp_valB, 'KE['+str(len(results[i]['KE']))+']'+'/D')
                branch_names.append('KE')
            if 'KEwidth' in results[i]:
                tmp_valC = array('d', [0]*len(results[i]['KEwidth']))
                arrayC = dict_tree.Branch('KEwidth', tmp_valC, 'KEwidth['+str(len(results[i]['KEwidth']))+']'+'/D')
                branch_names.append('KEwidth')
            if 'eff_means' in results[i]:
                tmp_valD = array('d', [0]*len(results[i]['eff_means']))
                arrayD = dict_tree.Branch('eff_means', tmp_valD, 'eff_means['+str(len(results[i]['eff_means']))+']'+'/D')
                branch_names.append('eff_means')
            if 'eff_errs' in results[i]:
                tmp_valE = array('d', [0]*len(results[i]['eff_errs']))
                arrayE = dict_tree.Branch('eff_errs', tmp_valE, 'eff_errs['+str(len(results[i]['eff_errs']))+']'+'/D')
                branch_names.append('eff_errs')
            #arrayB = dict_tree.Branch('KE', tmp_valB, 'KE/D')
            #arrayC = dict_tree.Branch('KEwidth', tmp_valC, 'KEwidth/D')
            for j in range(len(results[i][branch_names[0]])):
                if 'N' in results[i]:
                    tmp_valA[j] = results[i]['N'][j]
                if 'KE' in results[i]:
                    tmp_valB[j] = results[i]['KE'][j]
                if 'KEwidth' in results[i]:
                    tmp_valC[j] = results[i]['KEwidth'][j]
                if 'eff_means' in results[i]:
                    tmp_valD[j] = results[i]['eff_means'][j]
                if 'eff_errs' in results[i]:
                    tmp_valE[j] = results[i]['eff_errs'][j]

        else:
            tmp_sampled_val = array('d', [0])
            b = out_tree.Branch(names[i], tmp_sampled_val, names[i]+'/D')
            tmp_sampled_val[0] = results[i]
            b.Fill()
    dict_tree.Fill()
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
    elif sample_dict['prior_dist'] == 'randint':
        rand = np.random.randint(sample_dict['prior_params'][0], high=sample_dict['prior_params'][1]+1)
    elif sample_dict['prior_dist'] == 'loguniform':
        rand = np.power(10, np.random.uniform(sample_dict['prior_params'][0], sample_dict['prior_params'][1], 1))[0]
    else:
        logger.debug(dist_error)
        return None
    return rand


def _compute_transformed_inputs(func, inputs_dict, unitchange, transformed_dict):
    func_error = 'The {} function is not yet implemented in sample_inputs'.format(func)
    input_error = "Parameter needed to compute transformed inputs is missing"
    try:
        if 'Q' in inputs_dict:
            Q = inputs_dict['Q']
        elif 'Q_mean' in inputs_dict:
            Q = inputs_dict['Q_mean']
        if 'mass' in inputs_dict:
            mass = inputs_dict['mass']
        elif 'm_sum' in inputs_dict:
            mass = inputs_dict['m_sum']/2.
#        elif 'm_L' in inputs_dict:
#            cos2_th13 = inputs_dict['cos2_th13']
#            mass = (inputs_dict['m_L'] 
        if 'runtime' in inputs_dict:
            t = inputs_dict['runtime']
        if 'Q_spread' in inputs_dict:
            Q_spread = inputs_dict['Q_spread']
        sigma = inputs_dict['sigma']
    except:
        logger.debug(input_error)
    if func == 'm_H':
        return (inputs_dict['m_L']**2+inputs_dict['deltam2'])**0.5
    elif func == 'eta':
        cos2_th13 = inputs_dict['cos2_th13']
        if inputs_dict['MH']==0:
            eta = cos2_th13
        elif inputs_dict['MH']==1:
            eta = 1-cos2_th13
        return eta
    elif func == 'KEmin':
        if 'm_L' in inputs_dict:
            mass = (inputs_dict['eta']*inputs_dict['m_L']**2+(1-inputs_dict['eta'])*inputs_dict['m_H']**2)**0.5
        KEmin_mean = Q-mass-transformed_dict['window']
        #KEmin_mean = Q-transformed_dict['window']
        if transformed_dict['sample']==True:
            transformed_dict['prior_params'][0] = KEmin_mean
            KEmin_err = transformed_dict['prior_params'][1]
            if isinstance(KEmin_err, str):
                transformed_dict['prior_params'][1] = inputs_dict[KEmin_err]
            KEmin_s = _draw_random_sample(transformed_dict, "Check pre-sampling inputs for minimum energy.")
            return KEmin_s
        else:
            return KEmin_mean
    elif func == 'KEmin_1bin':
        KEmin_mean = ((8.*math.log(2))*(sigma**2+Q_spread**2))**0.5
        if transformed_dict['sample']==True:
            transformed_dict['prior_params'][0] = KEmin_mean
            KEmin_err = transformed_dict['prior_params'][1]
            if isinstance(KEmin_err, str):
                transformed_dict['prior_params'][1] = inputs_dict[KEmin_err]
            return _draw_random_sample(transformed_dict, "Check pre-sampling inputs for minimum energy.")
        else:
            return KEmin_mean
    elif func == 'A_s':
        if 'm_L' in inputs_dict:
            mass = (inputs_dict['eta']*inputs_dict['m_L']**2+(1-inputs_dict['eta'])*inputs_dict['m_H']**2)**0.5
        #br = 2.06278359*10**(-13)
        #br = 2.05844804e-13 + 6.34928332e-13*mass + 2.34357751e-13*mass**2 #From calculation of fraction of events in the last eV as a function of mass
        import P8_spectral_rate as P8sr
        KEmin = inputs_dict['KEmin']
        conv = 10**(-3)
        br = P8sr.frac_near_endpt(KEmin*10**(-3), Q*10**(-3), mass*10**(-3), transformed_dict['atom_or_mol'])
        Thalflife = 3.8789*10**8
        Nparticles = inputs_dict['Nparticles']
        A_s = Nparticles*np.log(2)/(Thalflife/10**12)*br
        return A_s
    elif func == 'KEmax':
        return Q+transformed_dict['window']
        #return Q
    elif func == 'S':
        if 'KEmin' in inputs_dict:
            KEmin = inputs_dict['KEmin']
        elif 'KEmin_1bin' in inputs_dict:
            KEmin = inputs_dict['KEmin_1bin']
        A_s = inputs_dict['A_s']
        return t*A_s
    elif func == 'B':
        if 'KEmin' in inputs_dict:
            KEmin = inputs_dict['KEmin']
        elif 'KEmin_1bin' in inputs_dict:
            KEmin = inputs_dict['KEmin_1bin']
        KEmax = inputs_dict['KEmax']
        if 'A_b' in inputs_dict:
            A_b = inputs_dict['A_b']
            return t*(KEmax-KEmin)*A_b
        elif 'B_1kev' in inputs_dict:
            B_1kev = inputs_dict['B_1kev']
            return B_1kev*(KEmax-KEmin)/1000.
        else:
            logger.debug(input_error)
    elif func == 'signal_frac':
        return inputs_dict['S']/(inputs_dict['S']+inputs_dict['B'])
    elif func == 'Ndata':
        #Appropriate for runs in which the number of data points sets the number of iterations.
        Ndata = 1
        while Ndata % transformed_dict['chains'] != 0:
            Ndata = np.random.poisson(inputs_dict['S']+inputs_dict['B'])
        return Ndata 
    elif func == 'data':
        #Should set this up to import a file and execute a function of the user's choosing
        simp_params = PhaseIIgen.load_simp_params(sigma, inputs_dict['scattering_prob'], Nscatters=inputs_dict['Nscatters'])
        #efficiency_dict = PhaseIIgen.load_efficiency_dict()
        if inputs_dict['scatter_type']==0:
            Kgen = PhaseIIgen.generate_unbinned_data(Q, mass, inputs_dict['KEmin'], inputs_dict['KEmax'], inputs_dict['S'], inputs_dict['B'], nsteps=5*10**4,lineshape='simplified', params=simp_params, efficiency_dict=None, err_from_B=inputs_dict['err_from_B'], interpolator=interp1d, convolver=convolve)
        elif inputs_dict['scatter_type']==1:
            Kgen = PhaseIIgen.generate_unbinned_data(Q, mass, inputs_dict['KEmin'], inputs_dict['KEmax'], inputs_dict['S'], inputs_dict['B'], nsteps=5*10**4,lineshape='detailed', params=simp_params[:2], efficiency_dict=None, err_from_B=inputs_dict['err_from_B'], interpolator=interp1d, convolver=convolve)
        else: 
            logger.info('Input "scatter_type"=0 for the simplified scattering model or "scatter_type"=1 for the detail model.')
        return {"KE":Kgen}

    elif func == 'efficiencies':
        efficiency_dict = PhaseIIgen.load_efficiency_dict()
        interp_eff, interp_eff_err = PhaseIIgen.efficiency_from_interpolation(inputs_dict['KE'], efficiency_dict, interp1d)
        return {"eff_means": interp_eff, "eff_errs": interp_eff_err}

    elif func == 'spectral_data':
        from scipy import integrate
        import P8_spectral_rate as P8sr
        conv = 10.**(-3)
        KEmin = inputs_dict['KEmin']*conv
        KEmax = inputs_dict['KEmax']*conv
        Q = Q*conv
        if transformed_dict['Nneutrinos'] == 2:
            eta = inputs_dict['eta']
            m_L = inputs_dict['m_L']*conv
            m_H = inputs_dict['m_H']*conv
            mass = (eta*m_L**2+(1-eta)*m_H**2)**0.5*conv
        else:
            mass = mass*conv
        sigma = sigma*conv
        Q_spread = Q_spread*conv

        extend = 7
        broadening = (Q_spread**2+sigma**2)**0.5
        E_max = Q-mass+extend*broadening
        if transformed_dict['Nneutrinos'] == 2:
            totalS = integrate.quad(P8sr.twonu_convolved_spectral_rate, KEmin-extend*broadening, KEmax, args=(Q, Q_spread, m_L, m_H, sigma, KEmin, eta), epsabs=1e-37, limit=100)[0]
        else:
            totalS = integrate.quad(P8sr.convolved_spectral_rate, KEmin-extend*broadening, KEmax, args=(Q, Q_spread, mass, sigma, KEmin), epsabs=1e-37, limit=100)[0]
        ##totalS = integrate.quad(P8sr.spectral_rate_in_window, KEmin-extend*broadening, KEmax, args=(Q, mass, KEmin), epsabs=1e-37, limit=100)[0]
        KEmax_eff = KEmax+extend*broadening
        totalB = integrate.quad(P8sr.convolved_bkgd_rate, KEmin-extend*broadening, KEmax_eff, args=(Q_spread, sigma, KEmin, KEmax))[0]
        bin_max = E_max
        bin_centers = [(KEmax_eff+bin_max)/2./conv]
        bin_widths = [(KEmax_eff-bin_max)/conv]
        lowEindex = len(transformed_dict['bin_region_widths'])-1
        #rate_past_endS = P8sr.convolved_spectral_rate(bin_centers[0], Q, Q_spread, mass, sigma, KEmin)
        if transformed_dict['Nneutrinos'] == 2:
            rate_past_endS = integrate.quad(P8sr.twonu_convolved_spectral_rate, E_max, KEmax_eff, args=(Q, Q_spread, m_L, m_H, sigma, KEmin, eta), epsabs=1e-37, limit=100)[0]
        else:
            rate_past_endS = integrate.quad(P8sr.convolved_spectral_rate, E_max, KEmax_eff, args=(Q, Q_spread, mass, sigma, KEmin))[0]
        ##rate_past_endS = integrate.quad(P8sr.spectral_rate_in_window, E_max, KEmax_eff, args=(Q, mass, KEmin))[0]
        rate_past_endB = integrate.quad(P8sr.convolved_bkgd_rate, E_max, KEmax_eff, args=(Q_spread, sigma, KEmin, KEmax))[0]
        bin_frac_signal = [rate_past_endS/totalS]
        bin_frac_bkgd = [rate_past_endB/totalB]

        for i in range(len(transformed_dict['bin_region_widths'])):
            if i == lowEindex:
                #bin_width = (E_max-np.sum(transformed_dict['bin_region_widths'][:lowEindex])-(KEmin-extend*broadening))/float(transformed_dict['nbins_per_region'][i])

                bin_width = (bin_min-(KEmin-extend*broadening))/float(transformed_dict['nbins_per_region'][i])
            else:
                bin_width = transformed_dict['bin_region_widths'][i]/float(transformed_dict['nbins_per_region'][i])
            for j in range(int(transformed_dict['nbins_per_region'][i])):
                bin_widths.append(bin_width/conv) #Converting back to meV
                bin_min = bin_max - bin_width
                bin_ctr = (bin_max+bin_min)/2.
                bin_centers.append(bin_ctr/conv) #Converting back to meV
                #if bin_width<0.0:
                #rateS = bin_width*P8sr.convolved_spectral_rate(bin_ctr, Q, Q_spread, mass, sigma, KEmin)
                #else
                if transformed_dict['Nneutrinos']==2:
                    rateS = integrate.quad(P8sr.twonu_convolved_spectral_rate, bin_min, bin_max, args=(Q, Q_spread, m_L, m_H, sigma, KEmin, eta), epsabs=1e-38, limit=150)[0]
                else:
                    rateS = integrate.quad(P8sr.convolved_spectral_rate, bin_min, bin_max, args=(Q, Q_spread, mass, sigma, KEmin), epsabs=1e-38, limit=150)[0]
                #rateS = integrate.quad(P8sr.spectral_rate_in_window, bin_min, bin_max, args=(Q, mass, KEmin), epsabs=1e-38, limit=150)[0]
                rateB = integrate.quad(P8sr.convolved_bkgd_rate, bin_min, bin_max, args=(Q_spread, sigma, KEmin, KEmax))[0]
                bin_frac_signal.append(rateS/totalS)
                bin_frac_bkgd.append(rateB/totalB)
                bin_max = bin_min

        tot = sum(bin_frac_signal)
        bin_frac_signal = [rate/tot for rate in bin_frac_signal]
        bin_frac_signal.reverse()
        bin_frac_bkgd.reverse()
        Ns = [np.random.poisson(inputs_dict['S']*fs) for fs in bin_frac_signal]
        #Ns = [int(inputs_dict['S']*fs) for fs in bin_frac_signal]
        Nb = [np.random.poisson(inputs_dict['B']*fb) for fb in bin_frac_bkgd]
        N = [ns + nb for ns, nb in zip(Ns, Nb)]
        #print("S:", inputs_dict['S'])
        #print("Ns:", sum(Ns))
        bin_centers.reverse()
        bin_widths.reverse()
        #print((max(bin_centers[:len(bin_centers)-1])-min(bin_centers))*10**(-3))
        #print(Q-mass-KEmin)
        """scaled_N = []
        for k in range(len(N)):
            scaled_N.append(N[k]/bin_widths[k])
        plt.plot(bin_centers, scaled_N)
        plt.show()
        plt.plot(bin_centers, N)
        #plt.show()"""
        return {'N':N, 'KE':bin_centers, 'KEwidth':bin_widths}

    elif func=='N':
        S_events = np.random.poisson(inputs_dict['S'])
        return [S_events*f for f in inputs_dict['bin_frac_signal']]
    else:
        logger.debug(func_error)
        return None

