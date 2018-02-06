"""Perform Stan diagnostic tests

Source: Michael Betancourt,
jupyter_case_studies/pystan_workflow/stan_utility.py 
Modified by Talia Weiss, 1-23-18

These tests are motivated here:
http://mc-stan.org/users/documentation/case-studies/pystan_workflow.html

Functions:
    check_div: Check how many transitions ended with a divergence
    check_treedepth: Check how many transitions failed due to tree depth
    check_energy: Check energy Bayesian fraction of missing information
    check_n_eff: Check the effective sample size per iteration
    check_rhat: Check the potential scale reduction factors
    check_all_diagnostics: Check all MCMC diagnosticcs
    partition_div: Get divergent and non-divergent parameter arrays
    compile_model: Cache Stan model
"""
try:
    import pystan
    import numpy
except:
    pass
import pickle


def check_div(fit):
    """Check how many transitions ended with a divergence

    Args:
        fit: stanfit object containing sampler output

    Returns:
        str: States the number of transitions that ended with a
            divergence
    """
    sampler_params = fit.get_sampler_params(inc_warmup=False)
    divergent = [x for y in sampler_params for x in y['divergent__']]
    n = sum(divergent)
    N = len(divergent)
    if n > 0:
        return('{} of {} iterations ended with a divergence ({}%).'.format(n, N,
            100 * n / N)+' Try running with larger adapt_delta to remove the divergences.')
    else:
        return('{} of {} iterations ended with a divergence ({}%).'.format(n, N,
            100 * n / N))

def check_treedepth(fit, max_depth = 10):
    """Check how many transitions ended prematurely due to tree depth

    A transition may end prematurely if the maximum tree depth limit is
    exceeded

    Args:
        fit: stanfit object containing sampler output
        max_depth: Maximum depth used to check tree depth

    Returns:
        str: States the number of transitions that passed the
            given max_depth.
    """
    sampler_params = fit.get_sampler_params(inc_warmup=False)
    depths = [x for y in sampler_params for x in y['treedepth__']]
    n = sum(1 for x in depths if x == max_depth)
    N = len(depths)
    if n > 0:
        return(('{} of {} iterations saturated the maximum tree depth of {}.'
               + ' ({}%)').format(n, N, max_depth, 100 * n / N)+' Run again with max_depth set to a larger value to avoid saturation.')
    else:
        return(('{} of {} iterations saturated the maximum tree depth of {}.'
            + ' ({}%)').format(n, N, max_depth, 100 * n / N))

def check_energy(fit):
    """Checks the energy Bayesian fraction of missing information (E-BFMI)

    Args:
        fit: stanfit object containing sampler output

    Returns:
       str: Warns that the model may need to be reparametrized if
           E-BFMI is less than 0.2
    """
    sampler_params = fit.get_sampler_params(inc_warmup=False)
    no_warning = True
    for chain_num, s in enumerate(sampler_params):
        energies = s['energy__']
        numer = sum((energies[i] - energies[i - 1])**2 for i in range(1, len(energies))) / len(energies)
        denom = numpy.var(energies)
        if numer / denom < 0.2:
            print('Chain {}: E-BFMI = {}'.format(chain_num, numer / denom))
            no_warning = False
    if no_warning:
        return('E-BFMI indicated no pathological behavior.')
    else:
        return('E-BFMI below 0.2 indicates you may need to reparameterize your model.')

def check_n_eff(fit):
    """Checks the effective sample size per iteration
    
    Args:
        fit: stanfit object containing sampler output

    Returns:
        str: States whether the effective sample size indicates
            an issue
    """
    fit_summary = fit.summary(probs=[0.5])
    n_effs = [x[4] for x in fit_summary['summary']]
    names = fit_summary['summary_rownames']
    n_iter = len(fit.extract()['lp__'])

    no_warning = True
    for n_eff, name in zip(n_effs, names):
        ratio = n_eff / n_iter
        if (ratio < 0.001):
            print('n_eff / iter for parameter {} is {}!'.format(name, ratio))
            print('E-BFMI below 0.2 indicates you may need to reparameterize your model.')
            no_warning = False
    if no_warning:
        return('n_eff / iter looks reasonable for all parameters.')
    else:
        return('  n_eff / iter below 0.001 indicates that the effective sample size has likely been overestimated.')

def check_rhat(fit):
    """Checks the potential scale reduction factors

    Args:
        fit: stan fit object containing sampler output

    Returns:
        str: States whether the Rhat values indicate an error
    """
    from math import isnan
    from math import isinf

    fit_summary = fit.summary(probs=[0.5])
    rhats = [x[5] for x in fit_summary['summary']]
    names = fit_summary['summary_rownames']

    no_warning = True
    for rhat, name in zip(rhats, names):
        if (rhat > 1.1 or isnan(rhat) or isinf(rhat)):
            print('Rhat for parameter {} is {}!'.format(name, rhat))
            no_warning = False
    if no_warning:
        return('Rhat looks reasonable for all parameters.')
    else:
        return('Rhat above 1.1 indicates that the chains very likely have not mixed.')

def check_all_diagnostics(fit):
    """Checks all MCMC diagnostics

    Args:
        fit: stanfit object containing sampler output

    Returns:
        list of str: Returns the strings indicating the results of the
            checks for divergence, treee depth, energy Bayesian fraction
            of missing energy, effective sample size, and Rhat
    """
    return(check_n_eff(fit) + '\n' + check_rhat(fit) + '\n' + check_div(fit)+ '\n' + check_treedepth(fit) + '\n' + check_energy(fit))

def _by_chain(unpermuted_extraction):
    num_chains = len(unpermuted_extraction[0])
    result = [[] for _ in range(num_chains)]
    for c in range(num_chains):
        for i in range(len(unpermuted_extraction)):
            result[c].append(unpermuted_extraction[i][c])
    return numpy.array(result)

def _shaped_ordered_params(fit):
    ef = fit.extract(permuted=False, inc_warmup=False) # flattened, unpermuted, by (iteration, chain)
    ef = _by_chain(ef)
    ef = ef.reshape(-1, len(ef[0][0]))
    ef = ef[:, 0:len(fit.flatnames)] # drop lp__
    shaped = {}
    idx = 0
    for dim, param_name in zip(fit.par_dims, fit.extract().keys()):
        length = int(numpy.prod(dim))
        shaped[param_name] = ef[:,idx:idx + length]
        shaped[param_name].reshape(*([-1] + dim))
        idx += length
    return shaped

def partition_div(fit):
    """ Returns parameter arrays for divergent and non-divergent transitions

    Args:
        fit: stanfit object containing sampler output
 
    Returns:
        (dict, dict): The first dictionary contains all nondivergent
            transitions, the second contains all divergent transitions
    """
    sampler_params = fit.get_sampler_params(inc_warmup=False)
    div = numpy.concatenate([x['divergent__'] for x in sampler_params]).astype('int')
    params = _shaped_ordered_params(fit)
    nondiv_params = dict((key, params[key][div == 0]) for key in params)
    div_params = dict((key, params[key][div == 1]) for key in params)
    return nondiv_params, div_params

def compile_model(filename, model_name=None, **kwargs):
    """Cache Stan model
    
    See http://pystan.readthedocs.io/en/latest/avoiding_recompilation.html

    Args:
        filename: Name of the input file containing the stan model code
        model_name: Name of the output cache file (default is model)
        kwargs: Not used

    Returns:
        pystan.StanModel: The Stan model is cached, and then the stan
            model is returned
    """
    from hashlib import md5

    with open(filename) as f:
        model_code = f.read()
        code_hash = md5(model_code.encode('ascii')).hexdigest()
        if model_name is None:
            cache_fn = 'cached-model-{}.pkl'.format(code_hash)
        else:
            cache_fn = 'cached-{}-{}.pkl'.format(model_name, code_hash)
        try:
            sm = pickle.load(open(cache_fn, 'rb'))
        except:
            sm = pystan.StanModel(model_code=model_code)
            with open(cache_fn, 'wb') as f:
                pickle.dump(sm, f)
        else:
            print("Using cached StanModel")
        return sm

