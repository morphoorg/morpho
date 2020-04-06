"""
Methods for computing analysis initialization and input values from saved data for Project 8 analyses.

Author: T. E. Weiss <tweiss@mit.edu>
Data: September 12, 2019
"""

import random

def sensitivity(sa):
    """
    Initializations for a spectral sensitivity analysis.
    """
    if 'Ndata' in sa.data:
        sa.iter = sa.data['Ndata']/sa.chains+sa.warmup
    if 'Q_init' in sa.data:
        sa.init[0]['Q'] = sa.data['Q_init']
        sa.init[0]['Q_mean'] = sa.data['Q_init']
    if 'sigma_init' in sa.data:
        sa.init[0]['sigma'] = sa.data['sigma_init']
    if 'sigma_ctr_init' in sa.data:
        sa.init[0]['sigma_ctr'] = sa.data['sigma_ctr_init']
    if 'mass_init' in sa.data:
        m_guess = sa.data['mass_init']+random.gauss(0, sa.data['max_m_guess_bias'])
        if m_guess>0:
            sa.init[0]['mass'] = m_guess
        else:
            sa.init[0]['mass'] = sa.data['min_mass']
    if 'm_L_init' in sa.data:
        m_guess = sa.data['m_L_init']+random.gauss(0, sa.data['max_m_guess_bias'])
        if m_guess>0:
            sa.init[0]['m_L'] = m_guess
        else:
            sa.init[0]['m_L'] = sa.data['min_mass']
    if 'KEmin_init' in sa.data:
        #sa.init[0]['KEmin'] = sa.data['Q_init']-sa.data['mass_init']-sa.data['window']
        sa.init[0]['KEmin'] = sa.data['KEmin_ctr']
    if 'A_b_init' in sa.data:
        sa.init[0]['A_b'] = sa.data['A_b_init']
    if 'A_s_init' in sa.data:
        sa.init[0]['A_s'] = sa.data['Ndata_for_conversion']/sa.data['runtime'] #Approximate conversion of Ndata to A_s
    if 'A2_init' in sa.data:
        sa.init[0]['A2'] = sa.init[0]['A_s']*sa.data['As_to_A2'] #Approximate conversion of A_s to A2 (spectral poisson rate) for a 1 eV window
    if 'A2ctr_from_As' in sa.data:
        sa.data['A2_ctr'] = sa.init[0]['A_s']*sa.data['As_to_A2']
    if 'A_s_ctr' in sa.data:
        #A_s_ctr is currently S
        sa.data['A_s_std'] = (sa.data['A_s_ctr'])**0.5/sa.data['runtime']
        #Redefining A_s_ctr
        sa.data['A_s_ctr'] = sa.data['A_s_ctr']/sa.data['runtime']  
