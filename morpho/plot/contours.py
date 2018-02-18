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
    Fix matrix formatting (including axes).
    Include histograms on top/left hand side.
    Color code histograms and create key.
    Contours at 1, 2, 3 sigma lines.
"""

import tempfile
import itertools as IT
import os
import pickle
import sys
try:
    import numpy as np
    from matplotlib.ticker import NullFormatter
    from matplotlib import cm

    import matplotlib as mpl
    mpl.rc('ytick', labelsize=8)
    mpl.rc('xtick', labelsize=8)
    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm
    from pylab import *
except ImportError:
    pass

def _gauss(x,y,Sigma,mu):
    X=np.vstack((x,y)).T
    mat_multi=np.dot((X-mu[None,...]).dot(np.linalg.inv(Sigma)),(X-mu[None,...]).T)
    return  np.diag(np.exp(-1*(mat_multi)))


def _plot_countour(x,y):

    z = _gauss(x, y, Sigma=np.asarray([[1.,.5],[0.5,1.]]), mu=np.asarray([0.,0.]))
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


def _plot_density(x, y, nbin=50):
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



def _matrix_plot(param_dict):

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
                    _plot_density(results[names[i]], results[names[j]], param_dict['nbin'])
                else:
                    _plot_density(results[names[i]], results[names[j]])
#                   _plot_contour(results[names[i]], results[names[j]])
    plt.tight_layout()
    plt.show()



def contours(param_dict):
    _matrix_plot(param_dict)
