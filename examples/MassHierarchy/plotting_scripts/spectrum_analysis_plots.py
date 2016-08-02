# spectrum_analysis_plots.py
#
# Author: T. E. Weiss
# Date: 27 July 2016
#
# Purpose:
# Create parameter traceplots and other related plots, as part of neutrino mass hierarchy analysis.
#

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
from pylab import *


#Unpickling stan fit object
with open('../cache/cached-model-9b564a72eea4422c25eed027ea785e5a.pkl', 'rb') as input1:
    pickle.load(input1)

with open('../results/analysis_fit_IH.pkl', 'rb') as input2:
    ModelFit = pickle.load(input2)

#Getting data from stan fit object
params = ModelFit.extract(permuted=True)
mbeta = params['mbeta']
min_mass = params['min_mass']


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


def readTTree(tree_path):
    myfile = ROOT.TFile(tree_path,"READ")
    tree = myfile.Get("analysis_parameters")

    mbeta = tree.mbeta
    min_mass = tree.min_mass
    log_likelihood = tree.LogLikelihood

    return mbeta, min_mass, log_likelihood

MH = 1
infile = '../results/MHtest_analyzer.root'
#mbeta_root, min_mass_root, log_likelihood_root = readTTree(infile)


#Plotting neutrino mass distributions
masses = ModelFit.plot(pars=['nu_mass'])
plt.tight_layout()
"""
if MH==0:
    plt.savefig(uniquify('./NH_numasses.pdf'))
elif MH==1:
    plt.savefig(uniquify('./IH_numasses.pdf'))
else:
    print "Cannot save plots. No mass hierarchy selected."
"""
plt.show()


#Plotting m_beta, the  lightest mass, and m_beta vs. the lightest mass
fig = plt.figure(figsize=(10,6))
a1 = plt.subplot(121)
ModelFit.plot(pars=['mbeta', 'min_mass'])
#plt.hist(mbeta, bins=45)
#a1.set_title(r'Histogram of Stan Output $m_\beta$ Values', fontsize=12.5)
#a1.set_xlabel(r'$m_\beta$ (eV)', fontsize=16)
#a2 = plt.subplot(221)
#plt.hist(min_mass, bins=45)
#a2.set_title(r'Histogram of Stan Output $M_{lightest}$ Values', fontsize=12.5)
#a2.set_xlabel(r'$M_{lightest}$ (eV)', fontsize=16)

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
"""
if MH==0:
    plt.savefig(uniquify('./NH_massparams.pdf'))
elif MH==1:
    plt.savefig(uniquify('./IH_massparams.pdf'))
"""
plt.show()


#Plotting neutrino mixing parameter distributions
mixing = ModelFit.plot(pars=['sin2_th12', 'sin2_th13', 'delta_m21', 'delta_m32', 'm32_withsign'])
plt.tight_layout()
"""
if MH==0:
    plt.savefig(uniquify('./NH_mixingparams.pdf'))
elif MH==1:
    plt.savefig(uniquify('./IH_mixingparams.pdf'))
"""
plt.show()
