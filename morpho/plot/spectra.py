#======================================================
# spectra.py
#
# Author: T. E. Weiss
# Date: Aug. 15, 2016
#
# Description:
#
# Plot beta decay spectra, by calculating its shape given a set of
# input parameters and/or by scatter plotting (KE, spectrum) pairs.
#
# In a configuration file plotting parameter dictionary, the user 
# should specify which plots he or she wishes to create using the 
# "plotting_options" list (e.g. "plotting_options": ["spectrum_shape",
# "spectrum_scatter", "overlay"]).
#=======================================================

"""
To do (for myself):
    Write function descriptions (comments).
    To make it easier to compare to generated spectrum, allow for root file inputs.
"""

import numpy as np
import matplotlib as mpl
mpl.rc('ytick', labelsize=8)
mpl.rc('xtick', labelsize=8)
import matplotlib.pyplot as plt
from pylab import *

import plotting_routines as pr


def spectrum_shape(KE, Q, Ue_squared, m_nu, time, activity, bkgd_rate):
    pure_spectrum = 0.0
    for i in range(len(Ue_squared)):
        if KE < (Q-abs(m_nu[i])):
            pure_spectrum += Ue_squared[i]*(Q-KE)*((KE-Q)**2-m_nu[i]**2)**0.5
    
    spectrum = time*(activity*pure_spectrum + bkgd_rate)

    return spectrum 


def plot_spectrum_scatter(x_data, spectrum, xlabel, color='b'):
    scatter(x_data, spectrum, marker='.', color=color)
    plt.title('Beta Decay Spectrum', fontsize=15)
    plt.xlabel(xlabel, fontsize=13)
    plt.ylabel('Count Rate', fontsize=13)


def plot_spectrum_shape(KEmin, KEmax, Q, Ue_squared, m_nu, time, activity, bkgd_rate, numKE=50, color='b'):
    KE = np.linspace(KEmin, KEmax, numKE)
    spectrum = []
    for KEval in KE:
        spectrum_val = spectrum_shape(KEval, Q, Ue_squared, m_nu, time, activity, bkgd_rate)
        spectrum.append(spectrum_val)
    plot_spectrum_scatter(KE, spectrum, "Kinetic Energy (eV)", color)


def read_from_param_list(data_names, params):
    data_vals = {}
    for key, val in data_names.items():
        if isinstance(val, (str)):
            if val in params:
                temp = params[val]
                if isinstance(temp, (tuple, list, set)):
                    data_vals[key] = np.mean(temp)
                elif isinstance(temp, (np.ndarray)):
                    data_vals[key] = np.mean(temp, axis=0)
                else:
                    data_vals[key] = temp
            else:
                if 'label' in key:
                    data_vals[key] = val
                else:
                    print(val + " must be a model fit parameter name or a plotting label.")
        elif isinstance(val, (int, float, long)):
            data_vals[key] = val
        else:
            print(val + " is of type " + type(val))
    
    return data_vals


def spectra(param_dict):
    # Determining which plots will be created and how they will be saved    
    plotting_options = param_dict['plotting_options']
    out_dir = param_dict['output_path']
    out_fmt = param_dict['output_format']
 
    # Unpickling stan fit object
    f = open(param_dict['read_cache_name'],'r')
    ModelFit, params = pr.unpickle_with_cache(f, param_dict['input_fit_name'])
    
    # Getting names of entries in Stan fit and particular data values necessary
    # for the spectrum calculation
    if 'data' in param_dict and param_dict['data']!='':
        data_names = param_dict['data']

    # Creating a dictionary of parameter values
    # Takes averages of elements of array-like objects in Stan fit
    data_vals = read_from_param_list(data_names, params)

    #Setting up error messages
    missing_key = "The 'data' dictionary in param_dict must contain the key(s) {}"
    required1 = set(('Q','Ue_squared', 'm_nu', 'time', 'activity', 'bkgd_rate'))
    required2 = set(('x_axis_data', 'spectrum_data', 'x_label'))
    required3 = required1 & required2

    #Getting x-axis range and number of points to be plotted, or setting to defaults
    if param_dict.has_key('x_range'):
        x_min = param_dict['x_range'][0]
        x_max = param_dict['x_range'][1]
    else:
        x_min = 18574.00
        x_max = 18575.05
    
    if param_dict.has_key('num_x'):
        num_x = param_dict['num_x']
    else:
        num_x = 50

    if 'spectrum_shape' in plotting_options:
        assert required1 <= set(data_vals), missing_key.format(required1)

        plot_spectrum_shape(x_min, x_max, data_vals['Q'], data_vals['Ue_squared'], data_vals['m_nu'], data_vals['time'], data_vals['activity'], data_vals['bkgd_rate'], num_x)
        plt.savefig(pr.uniquify(out_dir + '/spectrum_shape.' + out_fmt))
        plt.show()

    if 'spectrum_scatter' in plotting_options:
        assert required2 <= set(data_vals), missing_key.format(required2)

        plot_spectrum_scatter(params[data_names['x_axis_data']], params[data_names['spectrum_data']], data_vals['x_label'])
        plt.savefig(pr.uniquify(out_dir + '/spectrum_scatter.' + out_fmt))
        plt.show()

    if 'overlay' in plotting_options:
        assert required3 <= set(data_vals), missing_key.format(required3)

        plot_spectrum_shape
        plot_spectrum_shape(x_min, x_max, data_vals['Q'], data_vals['Ue_squared'], data_vals['m_nu'], data_vals['time'], data_vals['activity'], data_vals['bkgd_rate'], num_x)
        plot_spectrum_scatter(params[data_names['x_axis_data']], params[data_names['spectrum_data']], data_vals['x_label'], color='r')
        plt.savefig(pr.uniquify(out_dir + '/spectrum_shape_scatter.' + out_fmt))
        plt.show()
