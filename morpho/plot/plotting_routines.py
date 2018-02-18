#======================================================
# plotting_routines.py
#
# Author: T. E. Weiss
# Date: Aug. 15, 2016
#=======================================================

"""Private functions used in multiple plotting modules
"""

import tempfile
import itertools as IT
import os
import pickle

def _uniquify(path, sep = ''):
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


def _unpickle_with_cache(cache_name_file, fit_file):
    """
    Parameters:
    cache_name_file (str) - name of a file which contains the name of
    the cache file from the Stan run of interest.
    fit_file - name of the pickle file containing the fit from the Stan
    run of interest.

    Returns:
    ModelFit - a Stan fit object
    params - parameters in the Stan model, extracted from the fit.
    """
    cache_fn = cache_name_file.readline()
    with open(cache_fn, 'rb') as input1:
        pickle.load(input1)

    with open(fit_file, 'rb') as input2:
        ModelFit = pickle.load(input2)

    params = ModelFit.extract(permuted=True)
    
    return ModelFit, params

