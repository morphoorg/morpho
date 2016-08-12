#======================================================================
# contours.py
#
# Author: T. E. Weiss
# Date: Aug. 7, 2016
#
# Description:
#
# Create a matrix of contour/2D density plots for each combination of
# parameters in an analysis Stan model fit.
#======================================================================

"""
To do (for myself):
    Resolve ROOT/scipy compatibility issue.
    Put uniquify function in separate file.
    Fix matrix formatting (including axes).
    Include histograms on top/left hand side.
    Color code histograms and create key.
    Contours at 1, 2, 3 sigma lines.
"""

import numpy as np
import tempfile
import itertools as IT
import os
import pickle
import sys
from matplotlib.ticker import NullFormatter
from matplotlib import cm

import matplotlib as mpl
mpl.rc('ytick', labelsize=8)
mpl.rc('xtick', labelsize=8)
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import LogNorm
from pylab import *


def uniquify(path, sep = ''):
    """
    Each time a file is created the with same filename (in the same
    directory), add a consecutively higher number to the end of the
    filename.
    """
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


def gauss(x,y,Sigma,mu):
    X=np.vstack((x,y)).T
    mat_multi=np.dot((X-mu[None,...]).dot(np.linalg.inv(Sigma)),(X-mu[None,...]).T)
    return  np.diag(np.exp(-1*(mat_multi)))


def plot_countour(x,y):

    z = gauss(x, y, Sigma=np.asarray([[1.,.5],[0.5,1.]]), mu=np.asarray([0.,0.]))
    # define grid.
    xi = np.linspace(min(x),max(x),100)
    yi = np.linspace(min(y),max(y),100)
    ## grid the data.
    zi = griddata((x, y), z, (xi[None,:], yi[:,None]), method='cubic')
    levels = [0.2, 0.4, 0.6, 0.8, 1.0]
    # contour the gridded data, plotting dots at the randomly spaced data points
    CS = plt.contour(xi,yi,zi,len(levels),linewidths=0.5,colors='k', levels=levels)
    #CS = plt.contourf(xi,yi,zi,15,cmap=plt.cm.jet)
    CS = plt.contourf(xi,yi,zi,len(levels),cmap=cm.Greys_r, levels=levels)
    #plt.xlim(-2,2)
    #plt.ylim(-2,2)


def plot_density(x, y, nbin=50):
    """
    Creates 2D histogram of x and y, then displays this
    histogram as a 2D color gradient density plot.
        
    Parameters:
    x, y - array-like
    nbin - number of histogram bins along each direction (int)
    """
    H, xedges, yedges = np.histogram2d(y, x, range=[[min(y),max(y)], [min(x), max(x)]], bins=(nbin, nbin))
    extent = [yedges[0], yedges[-1], xedges[0], xedges[-1]]
    plt.imshow(H, extent=extent, cmap=cm.copper, norm=LogNorm(), aspect='auto')



def matrix_plot(param_dict):

    #Unpickling stan fit object
    cache_name_file = open(param_dict['read_cache_name'],'r')
    cache_fn = cache_name_file.readline()
    
    with open(cache_fn, 'rb') as input1:
        pickle.load(input1)
    
    with open(param_dict['input_fit_name'], 'rb') as input2:
        ModelFit = pickle.load(input2)
    results = ModelFit.extract(permuted=True)

    names = param_dict['result_names']
    npar = len(names)

    fig = plt.figure()    
    counter = 0
    for i in range(npar):
        for j, item in reversed(list(enumerate(names))):
            counter += 1
            if i<j:
                ax = fig.add_subplot(npar, npar, counter)
                ax.yaxis.tick_right()
                ax.ticklabel_format(style='sci',axis='both', scilimits=(-3, 0))
                if 'nbin' in param_dict:
                    plot_density(results[names[i]], results[names[j]], param_dict['nbin'])
                else:
                    plot_density(results[names[i]], results[names[j]])
#                    plot_contour(results[names[i]], results[names[j]])
    plt.tight_layout()
    plt.show()



def contours(param_dict):
    matrix_plot(param_dict)
