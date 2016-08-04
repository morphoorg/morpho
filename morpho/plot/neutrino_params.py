#======================================================
# neutrino_params.py
#
# Author: T. E. Weiss
# Date: Aug. 4, 2016
#
# Description:
#
# Create traceplots, sampling plots, and other related plots of
# neutrino mixing and mass parameters outputted by the analysis model.
#
# In a configuration file plotting parameter dictionary, the user 
# should specify which plots he or she wishes to create using the 
# "plotting_options" list (e.g. "plotting_options": ["neutrino_masses",
# "mass_params", "mixing_params"]).
#======================================================

"""
To do (for myself):
    Allow for more flexible and/or user defined ranges for plots of parameters.
    Allow for more flexible contour level inputs.
    Create a separate contour module.
    Clean up way of displaying error messages.
"""

import ROOT as ROOT
import numpy as np
import tempfile
import itertools as IT
import os
import pickle
import sys

import matplotlib as mpl
mpl.rc('ytick', labelsize=8)
mpl.rc('xtick', labelsize=8)
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import LogNorm
from pylab import *


<<<<<<< HEAD
def uniquify(path, sep = ''):
    """
    Each time a file is created the with same filename (in the same
    directory), add a consecutively higher number to the end of the
    filename.
    """
=======
#Each time file created with same filename (in same directory), adds consecutively higher number to end of filename
def uniquify(path, sep = ''):
>>>>>>> d5b33ee3c37f3f9560c25ab1a5ba471e9b8b9695
    def name_sequence():
        count = IT.count()
        yield ''
        while True:
            yield '{s}{n:d}'.format(s = sep, n = next(count))
    orig = tempfile._name_sequence
    with tempfile._once_lock:
        tempfile._name_sequence = name_sequence()
        path = os.path.normpath(path)
        dirname, basename = os.path.split(path)
        filename, ext = os.path.splitext(basename)
        fd, filename = tempfile.mkstemp(dir = dirname, prefix = filename, suffix = ext)
        tempfile._name_sequence = orig
    return filename


<<<<<<< HEAD
def plot_neutrino_masses(param_dict, ModelFit, data):
    """
    Creates, saves, and displays a plot of overlayed distributions
    for the three neutrino masses.
    Key: blue = m1, green = m2, red = m3.

    Parameters:
    param_dict - dictionary containing output path (str), output
    format (str), and optionally a specification of the mass
    hierarchy (str - either 'normal'or 'inverted').
    ModelFit - Stan fit object containing parameter distributions.
    data - dictionary with values providing the names of neutrino
    parameters used in the Stan model. Must contain a key 'nu_mass'.
    """
    out_dir = param_dict['output_path']
    out_fmt = param_dict['output_format']

=======
def plot_neutrino_masses(param_dict, ModelFit, data, out_dir):
>>>>>>> d5b33ee3c37f3f9560c25ab1a5ba471e9b8b9695
    masses = ModelFit.plot(pars=[data['nu_mass']])
    plt.tight_layout()
    
    if 'hierarchy' in param_dict and param_dict['hierarchy']!='':
<<<<<<< HEAD
        plt.savefig(uniquify(out_dir + './neutrino_masses_' + param_dict['hierarchy'] + '.' + out_fmt))
    else:
        plt.savefig(uniquify(out_dir + './neutrino_masses_real_data.' + out_fmt))
=======
        plt.savefig(uniquify(out_dir+'./neutrino_masses_' + param_dict['hierarchy'] + '.pdf'))
    else:
        plt.savefig(uniquify(out_dir+'./neutrino_masses_real_data.pdf'))
>>>>>>> d5b33ee3c37f3f9560c25ab1a5ba471e9b8b9695
        print("No mass hierarchy was selected.")
    plt.show()


<<<<<<< HEAD
def plot_mass_params(param_dict, ModelFit, data):
    """
    Creates, saves, and displays an image with three subplots:
    1) Stan distribution of m_beta.
    2) Stan distribution of the lightest neutrino mass.
    3) Scatter plot of the lightest neutrino mass vs. m_beta
       (the 'branching plot)

    Parameters:
    param_dict, ModelFit - same as above.
    data - dictionary with values providing the names of neutrino
    parameters used in the Stan model. Must contain keys 'mbeta'
    and 'min_mass'.
    """
    analysis_params = ModelFit.extract(permuted=True)
    out_dir = param_dict['output_path']
    out_fmt = param_dict['output_format']
=======
def plot_mass_params(param_dict, ModelFit, data, out_dir):
    analysis_params = ModelFit.extract(permuted=True)
>>>>>>> d5b33ee3c37f3f9560c25ab1a5ba471e9b8b9695

    mbeta = analysis_params[data['mbeta']]
    min_mass = analysis_params[data['min_mass']]
            
    fig = plt.figure(figsize=(10,6))
    a1 = plt.subplot(121)
    ModelFit.plot(pars=[data['mbeta'], data['min_mass']])
    
    b = plt.subplot(122)
    scatter(min_mass, mbeta, marker='.', color='r')
    plt.title(r'Lightest Neutrino Mass vs. $m_\beta$', fontsize=15)
    plt.xlabel(r'$M_{lightest}$ (eV)', fontsize=16)
    plt.ylabel(r'$M_\beta$ (eV)', fontsize=16)
    plt.ylim(0.003, 3)
    plt.xlim(1E-3, 1)
    plt.xscale('log')
    plt.yscale('log')
    plt.tight_layout()
                
    if 'hierarchy' in param_dict and param_dict['hierarchy']!='':
<<<<<<< HEAD
        plt.savefig(uniquify(out_dir +'./mass_params_' + param_dict['hierarchy'] + '.' + out_fmt))
    else:
        plt.savefig(uniquify(out_dir+'./mass_params_real_data.' + out_fmt))
=======
        plt.savefig(uniquify(out_dir+'./mass_params_' + param_dict['hierarchy'] + '.pdf'))
    else:
        plt.savefig(uniquify(out_dir+'./mass_params_real_data.pdf'))
>>>>>>> d5b33ee3c37f3f9560c25ab1a5ba471e9b8b9695
    
    plt.show()


<<<<<<< HEAD
def plot_mixing_params(param_dict, ModelFit, data):
    """
    Creates, saves, and displays an image containing parameter
    distribtion plots and Stan sampling plots (parameter value vs.
    number of iterations, to demonstrate convergence) for neutrino
    mixing parameters.

    Parameters:
    param_dict, ModelFit - same as above.
    data - dictionary with values providing the names of neutrino
    parameters used in the Stan model. Must contain keys 'sin2_th12',
    'sin2_th13', 'delta_m21', 'delta_m32', 'm32_with_sign'.
    """
    out_dir = param_dict['output_path']
    out_fmt = param_dict['output_format']

=======
def plot_mixing_params(param_dict, ModelFit, data, out_dir):
>>>>>>> d5b33ee3c37f3f9560c25ab1a5ba471e9b8b9695
    mixing = ModelFit.plot(pars=[data['sin2_th12'], data['sin2_th13'], data['delta_m21'], data['delta_m32'], data['m32_withsign']])
    plt.tight_layout()

    if 'hierarchy' in param_dict and param_dict['hierarchy']!='':
<<<<<<< HEAD
        plt.savefig(uniquify(out_dir + './mixing_params_' + param_dict['hierarchy'] + '.' + out_fmt))
    else:
        plt.savefig(uniquify(out_dir + './mixing_params_real_data.' + out_fmt))
    plt.show()


def plot_contours(ModelFit, param_dict, data):
    """
    Combines distributions from pairs of parameters to create 2D
    histograms.

    Then creates, saves, and displays an image with two subplots:
    1) delta_m21 vs. sin2_th12
    2) sin2_th13 vs. sin2_th12
    Each subplot contains a 2D color-gradient density plot with
    overlayed contours at locations with particular numbers of
    points (to be improved).

    Parameters:
    param_dict, ModelFit - same as above.
    data - dictionary with values providing the names of neutrino
    parameters used in the Stan model. Must contain keys 'delta_m21',
    'sin2_th12', and 'sin2_th13'.
    """
    analysis_params = ModelFit.extract(permuted=True)
    out_dir = param_dict['output_path']
    out_fmt = param_dict['output_format']
=======
        plt.savefig(uniquify(out_dir+'./mixing_params_' + param_dict['hierarchy'] + '.pdf'))
    else:
        plt.savefig(uniquify(out_dir+'./mixing_params_real_data.pdf'))
    plt.show()


def plot_contours(ModelFit, param_dict, data, out_dir):

    analysis_params = ModelFit.extract(permuted=True)
>>>>>>> d5b33ee3c37f3f9560c25ab1a5ba471e9b8b9695

    delta_m21 = analysis_params[data['delta_m21']]
    sin2_th12 = analysis_params[data['sin2_th12']]
    sin2_th13 = analysis_params[data['sin2_th13']]
            
    fig = plt.figure()
    ax = fig.add_subplot(121)
    H, xedges, yedges = np.histogram2d(delta_m21,sin2_th12, range=[[5E-5,1.E-4], [0.1, 0.39]], bins=(50, 50))
    extent = [yedges[0], yedges[-1], xedges[0], xedges[-1]]
    subplots_adjust(bottom=0.15, left=0.15)
    plt.imshow(H, extent=extent ,cmap=cm.copper, norm=LogNorm(), aspect='auto')
    plt.colorbar()
    levels = (5., 100., 350.)
    cset = contour(H, levels, origin='lower',colors=['blue','green','red'],linewidths=(1.9, 1.6, 1.5, 1.4),extent=extent)
    plt.clabel(cset, inline=1, fontsize=10, fmt='%1.0i')
    plt.xlabel(r'$sin^2(\theta_{12})$', fontsize=16)
    plt.ylabel(r'$\Delta m^2_{21}$', fontsize=16)
    for c in cset.collections:
        c.set_linestyle('solid')

    ax2 = fig.add_subplot(122)
    Hb, xedgesb, yedgesb = np.histogram2d(sin2_th13,sin2_th12, range=[[0.0, 0.08], [0.1, 0.39]], bins=(50, 50))
    extentb = [yedgesb[0], yedgesb[-1], xedgesb[0], xedgesb[-1]]
    subplots_adjust(bottom=0.15, left=0.15)
    plt.imshow(Hb, extent=extentb, origin='lower', cmap=cm.copper, norm=LogNorm(), aspect='auto')
    plt.colorbar()
    levels = (5., 100., 350.)
    cset = contour(Hb, levels, origin='lower',colors=['blue','green','red'],linewidths=(1.9, 1.6, 1.5, 1.4),extent=extentb)
    plt.clabel(cset, inline=1, fontsize=10, fmt='%1.0i')
    plt.xlabel(r'$sin^2(\theta_{12})$', fontsize=16)
    plt.ylabel(r'$sin^2(\theta_{13})$', fontsize=16)
    for c in cset.collections:
       c.set_linestyle('solid')

    plt.tight_layout()

    if 'hierarchy' in param_dict and param_dict['hierarchy']!='':
<<<<<<< HEAD
        plt.savefig(uniquify(out_dir + './mixing_param_contours_' + param_dict['hierarchy'] + '.' + out_fmt))
    else:
        plt.savefig(uniquify(out_dir + './mixing_param_contours_real_data.' + out_fmt))
=======
        plt.savefig(uniquify(out_dir + './mixing_param_contours_' + param_dict['hierarchy'] + '.pdf'))
    else:
        plt.savefig(uniquify(out_dir + './mixing_param_contours_real_data.pdf'))
>>>>>>> d5b33ee3c37f3f9560c25ab1a5ba471e9b8b9695
    plt.show()


def neutrino_params(param_dict):
<<<<<<< HEAD
    """
    Loads a Stan ModelFit from a pickle file. Then invokes whichever
    plotting functions are indicated by the 'plotting_options':[opt1, opt2 ...]
    entry in param dict.

    Possible options: 'neutrino_masses', 'mass_params', 'mixing_params',
    'contours'.

    Parameters:
    param_dict - dictionary containing output path (str), output
    format (str), name of a file containing the cache filename (str),
    name of a pickle file (str), a 'data' dictionary with names of Stan
    parameters, 'plotting_options' (list), and optionally a specification
    of the mass hierarchy (str - either 'normal'or 'inverted')
    """    
=======
>>>>>>> d5b33ee3c37f3f9560c25ab1a5ba471e9b8b9695

    #Determining which plots will be created
    plotting_options = param_dict['plotting_options']

    #Unpickling stan fit object
    cache_name_file = open(param_dict['read_cache_name'],'r')
    cache_fn = cache_name_file.readline()
    
    with open(cache_fn, 'rb') as input1:
        pickle.load(input1)

    with open(param_dict['input_fit_name'], 'rb') as input2:
        ModelFit = pickle.load(input2)

    #Getting names of data entries in Stan fit
    if 'data' in param_dict and param_dict['data']!='':
        data = param_dict['data']

<<<<<<< HEAD
    #Plotting neutrino mass distributions
    if 'neutrino_masses' in plotting_options:
        if 'nu_mass' in data and data['nu_mass']!='':
            plot_neutrino_masses(param_dict, ModelFit, data)
=======
    out_dir = param_dict['output_path']

    
    #Plotting neutrino mass distributions
    if 'neutrino_masses' in plotting_options:
        if 'nu_mass' in data and data['nu_mass']!='':
            plot_neutrino_masses(param_dict, ModelFit, data, out_dir)
>>>>>>> d5b33ee3c37f3f9560c25ab1a5ba471e9b8b9695

        else:
            print("Cannot plot neutrino_masses if parameter 'nu_mass' is not specified in param_dict['data'].")
    
    
    #Plotting m_beta, the  lightest mass, and m_beta vs. the lightest mass
    if 'mass_params' in plotting_options:
        if 'mbeta' not in data or data['mbeta']=='':
            print("Cannot plot mass_params if parameter 'm_beta' is not specified in param_dict['data'].")

        elif 'min_mass' not in data or data['min_mass']=='':
            print("Cannot plot mass_params if parameter 'min_mass' is not specified in param_dict['data'].")

        else:
<<<<<<< HEAD
            plot_mass_params(param_dict, ModelFit, data)
=======
            plot_mass_params(param_dict, ModelFit, data, out_dir)
>>>>>>> d5b33ee3c37f3f9560c25ab1a5ba471e9b8b9695
    
    
    #Plotting neutrino mixing parameter distributions
    if 'mixing_params' in plotting_options:
        
        if 'sin2_th12' and 'sin2_th13' and 'delta_m21' and 'delta_m32' and 'm32_withsign' in data:
<<<<<<< HEAD
            plot_mixing_params(param_dict, ModelFit, data)
=======
            plot_mixing_params(param_dict, ModelFit, data, out_dir)
>>>>>>> d5b33ee3c37f3f9560c25ab1a5ba471e9b8b9695

        else:
            print("Cannot plot mixing_params if not all mixing parameters specified in param_dict['data']")


    #Mixing parameter contour plots
    if 'contours' in plotting_options:
    
        if 'delta_m21' and 'sin2_th12' and 'sin2_th13' in data:
<<<<<<< HEAD
            plot_contours(ModelFit, param_dict, data)
=======
            plot_contours(ModelFit, param_dict, data, out_dir)
>>>>>>> d5b33ee3c37f3f9560c25ab1a5ba471e9b8b9695

        else:
            print("Cannot plot contours if 'delta_m21', 'sin2_th12', or 'sin2_th13' are not specified in param_dict['data'].")
    print("finished")


