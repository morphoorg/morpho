#======================================================
# spectra.py
#
# Author: T. E. Weiss
# Date: Aug. 15, 2016
#
# Description:
#
# Plot beta decay spectra, by calculating a spectral shape given a set
# of input parameters and/or by scatter plotting (KE, spectrum) pairs.
#
# In a configuration file plotting parameter dictionary, the user 
# should specify which plots he or she wishes to create using the 
# "plotting_options" list (e.g. "plotting_options": ["spectrum_shape",
# "spectrum_scatter", "overlay"]).
#=======================================================



import numpy as np
import matplotlib as mpl
mpl.rc('ytick', labelsize=8)
mpl.rc('xtick', labelsize=8)
import matplotlib.pyplot as plt
from pylab import *

import plotting_routines as pr


def spectrum_shape(KE, Q, Ue_squared, m_nu, time, activity, bkgd_rate):
    """
    Calculates and returns a beta decay spectral rate dN/dE
    at a particular kinetic energy 'KE' for a time period 'time.'

    Parameters:
    KE (float) in eV; endpoint (float) Q in eV;
    electron neutrino PMNS matrix elements squared Ue_squared (vector);
    neutrino masses m_nu (vector); time (float) in s,
    tritium activity (float) in /s; bkgd_rate (float) in /eV/s
    """
    pure_spectrum = 0.0
    for i in range(len(Ue_squared)):
        if KE < (Q-abs(m_nu[i])):
            pure_spectrum += Ue_squared[i]*(Q-KE)*((KE-Q)**2-m_nu[i]**2)**0.5
    
    spectrum = time*(activity*pure_spectrum + bkgd_rate)

    return spectrum 


def plot_spectrum_scatter(x_data, spectrum, xlabel, color='b', yscale='linear'):
    """
    Creates a scatter plot, with a spectrum count rate on the
    y-axis and either energy or frequency on the x-axis.

    Parameters:
    x_data - vector of kinetic energy or frequency data points.
    spectrum - vector of count rates
    x_label - x-axis plot label (str); color - color of points 
    """
    scatter(x_data, spectrum, marker='.', color=color)
    plt.title('Beta Decay Spectrum', fontsize=15)
    plt.xlabel(xlabel, fontsize=13)
    plt.ylabel('Count Rate', fontsize=13)
    plt.yscale(yscale)


def plot_spectrum_shape(KEmin, KEmax, Q, Ue_squared, m_nu, time, activity, bkgd_rate, numKE=50, color='b', yscale='linear'):
    """
    Generates numKE evenly spaced kinetic energy values in the range
    [KEmin, KEmax], associates to each of them a spectral rate using
    spectrum_shape, and creates a scatter plot of the (KE, spectrum)
    pairs using plot_spectrum_scatter.
    """
    KE = np.linspace(KEmin, KEmax, numKE)
    spectrum = []
    for KEval in KE:
        spectrum_val = spectrum_shape(KEval, Q, Ue_squared, m_nu, time, activity, bkgd_rate)
        spectrum.append(spectrum_val)
    plot_spectrum_scatter(KE, spectrum, "Kinetic Energy (eV)", color, yscale)


def read_from_param_list(data_names, params):
    """
    Parameters:
    data_names - dictionary with string values that name entries in
    params. Can also contain plot labels and numbers (int, float, etc.).
    params - array of parameters extracted from a Stan fit object

    Creates a dictionary data_vals with entries of the form
    {"data_name":avg_data_value}. The keys are the same as in data_names,
    but the values differ as follows:

    1) If the value is a string that names an object in params, the value
       in data_vals will be the mean of the object's entries.
    2) If the value is a string (not in params) and the key contains 'label',
       the value in data_vals will stay the same as in data_names (to allow
       for easy plot labelling).
    3) If the value in data_names is already numerical, it will stay the same
       (to allow for the incorporation of values absent from the Stan fit).
    """
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
    """
    Unpickles a Stan fit object. Creates from data_names a new dictionary
    data_vals that is useful for spectral shape plotting. Then invokes
    whichever plotting functions are indicated by "plotting_options."

    Possible options: 'spectrum_shape', 'spectrum_scatter', 'overlay'

    Parameters:
    param_dict - dictionary containing output path (str), output
    format (str), name of a file containing the cache filename (str),
    name of a pickle file (str), a 'data_names' dictionary with useful
    values, plot labels, and names of Stan parameters,  'plotting_options'
    (list), x_range (list), y_scale (str), and optionally num_x (int)
    """

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

    # Setting up error messages
    missing_key = "The 'data' dictionary in param_dict must contain the key(s) {}"
    required1 = set(('Q','Ue_squared', 'm_nu', 'time', 'activity', 'bkgd_rate'))
    required2 = set(('x_axis_data', 'spectrum_data', 'x_label'))
    required3 = required1 & required2

    # Establishing x-axis range, number of points to be plotted, and yscale
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

    if param_dict.has_key('y_scale'):
        yscale = param_dict['y_scale']
    else:
        yscale = 'linear'

    # Plotting
    if 'spectrum_shape' in plotting_options:
        assert required1 <= set(data_vals), missing_key.format(required1)

        plot_spectrum_shape(x_min, x_max, data_vals['Q'], data_vals['Ue_squared'], data_vals['m_nu'], data_vals['time'], data_vals['activity'], data_vals['bkgd_rate'], num_x, yscale=yscale)
       # plt.savefig(pr.uniquify(out_dir + '/spectrum_shape.' + out_fmt))
        plt.show()

    if 'spectrum_scatter' in plotting_options:
        assert required2 <= set(data_vals), missing_key.format(required2)

        plot_spectrum_scatter(params[data_names['x_axis_data']], params[data_names['spectrum_data']], data_vals['x_label'], yscale=yscale)
      #  plt.savefig(pr.uniquify(out_dir + '/spectrum_scatter.' + out_fmt))
        plt.show()

    if 'overlay' in plotting_options:
        assert required3 <= set(data_vals), missing_key.format(required3)

        plot_spectrum_scatter(params[data_names['x_axis_data']], params[data_names['spectrum_data']], data_vals['x_label'], color='r', yscale=yscale)
        plot_spectrum_shape(x_min, x_max, data_vals['Q'], data_vals['Ue_squared'], data_vals['m_nu'], data_vals['time'], data_vals['activity'], data_vals['bkgd_rate'], num_x, yscale=yscale)
        plt.savefig(pr.uniquify(out_dir + '/spectrum_shape_scatter.' + out_fmt))
        plt.show()
