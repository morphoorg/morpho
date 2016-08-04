# spectrum_analysis_plots.py
#
# Author: T. E. Weiss
# Date: 27 July 2016
#
# Purpose:
# Create parameter traceplots and other related plots, as part of neutrino mass hierarchy analysis.
#


"""
To do (for myself):
    Include better descriptions of different plotting options/how this module works.
    Allow for more flexible and/or user defined ranges for plots of parameters.
    Allow for more flexible contour level inputs.
    Create a separate contour module.
    Fix the problem where I write cache file names to many text files. (Current plan: append to existing text file in appropriate location.)
    Clean up error messafe situation.
    Incorporate output format choice.
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


#Each time file created with same filename (in same directory), adds consecutively higher number to end of filename
def uniquify(path, sep = ''):
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


def plot_neutrino_masses(param_dict, ModelFit, data, out_dir):
    masses = ModelFit.plot(pars=[data['nu_mass']])
    plt.tight_layout()
    
    if 'hierarchy' in param_dict and param_dict['hierarchy']!='':
        plt.savefig(uniquify(out_dir+'./neutrino_masses_' + param_dict['hierarchy'] + '.pdf'))
    else:
        plt.savefig(uniquify(out_dir+'./neutrino_masses_real_data.pdf'))
        print("No mass hierarchy was selected.")
    plt.show()


def plot_mass_params(param_dict, ModelFit, data, out_dir):
    analysis_params = ModelFit.extract(permuted=True)

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
        plt.savefig(uniquify(out_dir+'./mass_params_' + param_dict['hierarchy'] + '.pdf'))
    else:
        plt.savefig(uniquify(out_dir+'./mass_params_real_data.pdf'))
    
    plt.show()


def plot_mixing_params(param_dict, ModelFit, data, out_dir):
    mixing = ModelFit.plot(pars=[data['sin2_th12'], data['sin2_th13'], data['delta_m21'], data['delta_m32'], data['m32_withsign']])
    plt.tight_layout()

    if 'hierarchy' in param_dict and param_dict['hierarchy']!='':
        plt.savefig(uniquify(out_dir+'./mixing_params_' + param_dict['hierarchy'] + '.pdf'))
    else:
        plt.savefig(uniquify(out_dir+'./mixing_params_real_data.pdf'))
    plt.show()


def plot_contours(ModelFit, param_dict, data, out_dir):

    analysis_params = ModelFit.extract(permuted=True)

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
        plt.savefig(uniquify(out_dir + './mixing_param_contours_' + param_dict['hierarchy'] + '.pdf'))
    else:
        plt.savefig(uniquify(out_dir + './mixing_param_contours_real_data.pdf'))
    plt.show()


def neutrino_params(param_dict):

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

    out_dir = param_dict['output_path']

    
    #Plotting neutrino mass distributions
    if 'neutrino_masses' in plotting_options:
        if 'nu_mass' in data and data['nu_mass']!='':
            plot_neutrino_masses(param_dict, ModelFit, data, out_dir)

        else:
            print("Cannot plot neutrino_masses if parameter 'nu_mass' is not specified in param_dict['data'].")
    
    
    #Plotting m_beta, the  lightest mass, and m_beta vs. the lightest mass
    if 'mass_params' in plotting_options:
        if 'mbeta' not in data or data['mbeta']=='':
            print("Cannot plot mass_params if parameter 'm_beta' is not specified in param_dict['data'].")

        elif 'min_mass' not in data or data['min_mass']=='':
            print("Cannot plot mass_params if parameter 'min_mass' is not specified in param_dict['data'].")

        else:
            plot_mass_params(param_dict, ModelFit, data, out_dir)
    
    
    #Plotting neutrino mixing parameter distributions
    if 'mixing_params' in plotting_options:
        
        if 'sin2_th12' and 'sin2_th13' and 'delta_m21' and 'delta_m32' and 'm32_withsign' in data:
            plot_mixing_params(param_dict, ModelFit, data, out_dir)

        else:
            print("Cannot plot mixing_params if not all mixing parameters specified in param_dict['data']")


    #Mixing parameter contour plots
    if 'contours' in plotting_options:
    
        if 'delta_m21' and 'sin2_th12' and 'sin2_th13' in data:
            plot_contours(ModelFit, param_dict, data, out_dir)

        else:
            print("Cannot plot contours if 'delta_m21', 'sin2_th12', or 'sin2_th13' are not specified in param_dict['data'].")
    print("finished")


