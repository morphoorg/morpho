'''
Processor for calibrating results; i.e., determining how often posteriors are consistent with "true" values assumed to generate fake data.
Useful for sensitivity analyses.

Authors: T. E. Weiss
Date: May 2020
'''

from __future__ import absolute_import

import numpy as np
import math
from os.path import exists

from morpho.utilities import morphologging, reader
from morpho.processors import BaseProcessor
from morpho.processors.IO import IOROOTProcessor
logger = morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)


class CalibrationProcessor(BaseProcessor):
    '''
    Performs a Bayesian sensitivity calibration for a continuous parameter - i.e., computes the coverage of a credible interval. Uses either an upper limit or upper and lower bounds on a posterior, depending on user input. Prints the coverage as well as (optionally) the median and mean credible windows.
    
    Required input:
        files: List of strings naming ROOT files produced by an ensemble of morpho runs.
        in_param_names: List of strings naming parameters of interest inputted to the generator.
        
    Optional input:
        cred_interval: List with float elements between 0 and 1 defining a posterior credible window; defaults to [0.05, 0.95]. If len(cred_interval)==1, this procesor finds the coverage of a limit. If len(cred_interval)==2, it finds the coverage of an interval.
        root_in_tree: Tree containing data generation input values in each file. Defaults to "input".
        root_post_tree: Tree containing analysis posteriors. Defaults to "analysis".
        post_param_names: List of strings naming posteriors produced by Stan analysis for a parameters of interest. Defaults to self.in_param_names.
        quantile: If True, compute quantile credible intervals. Otherwise, compute highest density intervals.
        check_if_nonzero: If True, check whether posteriors allow the parameters to be distinguished from zero (given some credible interval).
        
    Results:
        coverages: dictionary containing coverage of interval given by self.cred_interval, for each parameter in self.in_param_names
    '''
    def InternalConfigure(self,params):
        #Required input
        self.files = reader.read_param(params,'files','required')
        self.in_param_names = reader.read_param(params,'in_param_names','required')
        
        #Optional input
        self.cred_interval = reader.read_param(params,'cred_interval',[0.05, 0.95])
        self.root_in_tree = reader.read_param(params,'root_in_tree','input')
        self.root_post_tree = reader.read_param(params,'root_post_tree','analysis')
        self.post_param_names = reader.read_param(params,'post_param_names',self.in_param_names)
        self.quantile = reader.read_param(params,'quantile',False)
        self.check_if_nonzero = reader.read_param(params,'check_if_nonzero',False)
        
        #Other
        self.failed_runs = []

        # Checking the existence of files (non blocking if missing file)
        for file in self.files:
            if not exists(file):
                logger.warning("File {} doesn't exist".format(file))
        return True
    
    
    def perform_calibration(self):
        logger.info("Calibrating credible interval results")
        
        #Defining credibility
        if len(self.cred_interval)==1:
            alpha = self.cred_interval[0]
        elif len(self.cred_interval)==2:
            alpha = self.cred_interval[1]-self.cred_interval[0]
        else:
            logger.error("Input a credible interval list with one or two elements.")
            return
        
        #Setting up variables before loop
        calib_bounds = {name:[] for name in self.in_param_names}
        consistent_with_zero = {name:0 for name in self.in_param_names}
        n_recovered_inputs = {name:0 for name in self.in_param_names}
        #Dictionary to keep track of sums of quantities, so that averages can be taken after the loop
        sums = {name:dict.fromkeys(['median', 'mean', 'lower', 'upper'],0) for name in self.in_param_names}
        
        for i, filename in enumerate(self.files): 
            #Reading input values and posteriors from root files
            try:
                input_vals, posterior_arrays = self._load_inputs_and_posteriors(filename)
            except AttributeError as error:
                logger.warning(error)
                self.failed_runs.append(filename)
                pass
            except RuntimeError as error:
                logger.warning("Caught processor error; passing...")
                pass
            
            #Constructing credible intervals
            logger.debug("Constructing credible intervals")
            if self.quantile == True:
                for param_name in calib_bounds:
                    calib_bounds[param_name].append(self._get_quantile_bounds(posterior_arrays[param_name]))
            else:
                for param_name in calib_bounds:
                    bounds = self._get_highest_density_bounds(posterior_arrays[param_name], alpha)
                    calib_bounds[param_name].append(bounds)
                    #Consistency-with-zero checks are only possible for HDIs
                    if bounds[0] == 0.0:
                        consistent_with_zero[param_name] += 1
            
            #Tracking and optionally printing information about the intervals
            bs={key:val[i] for key, val in calib_bounds.items()}
            logger.debug('\n---------------------EXPERIMENT #{}:---------------------'.format(i))
            self._report_post_param_info(input_vals, posterior_arrays, bs, sums)
            logger.debug('\n--------------------------------------------------------')
                
            #Determining whether intervals contain inputted values
            for param_name in calib_bounds:
                if len(self.cred_interval) == 1:
                    if input_vals[param_name] <= bs[param_name][0]:
                        n_recovered_inputs[param_name] += 1
                elif len(self.cred_interval) == 2:
                    if bs[param_name][0] <= input_vals[param_name] <= bs[param_name][1]:
                        n_recovered_inputs[param_name] += 1
            
        #Calculating an interval coverage for each parameter
        for run in self.failed_runs:
            self.files.remove(run)
        coverages = {p:n_recovered_inputs[p]/float(len(self.files)) for p in self.in_param_names}
        
        #Reporting calibration results
        self._report_calibration_results(calib_bounds, consistent_with_zero, coverages, sums)
        
        return coverages
        

    def _load_inputs_and_posteriors(self, filename):
        """
        For a given root file, returns two dictionaries, one containing inputted values and the other containing posterior arrays.
        """
        logger.debug("Reading input values and posterior arrays")
        in_reader_config = {
            "action": "read",
            "tree_name": self.root_in_tree,
            "filename": filename,
            "variables": self.in_param_names
        }
        post_reader_config = {
            "action": "read",
            "tree_name": self.root_post_tree,
            "filename": filename,
            "variables": self.post_param_names
        }
        rin, rpost = IOROOTProcessor("reader"), IOROOTProcessor("reader2")
        if not rin.Configure(in_reader_config):
            logger.warning("Failed to Configure <{}> processor".format(rin.name))
            raise RuntimeError
        if not rpost.Configure(post_reader_config):
            logger.warning("Failed to Configure <{}> processor".format(rpost.name))
            raise RuntimeError
        if not rin.Run():
            logger.warning("Failed to Run <{}> processor".format(rin.name))
            raise RuntimeError
        if not rpost.Run():
            logger.warning("Failed to run <{}> processor".format(rpost.name))
            raise RuntimeError
        input_vals = {key:val[0] for key, val in rin.data.items()}
        posterior_arrays = rpost.data
        return input_vals, posterior_arrays


    def _get_quantile_bounds(self, posterior_array):
        """
        Input:
            posterior_array: a list or array of posterior values
        
        From self:
            self.cred_interval: a list [a, b] for 0<=a,b<=1. For example, a 90% credible interval would be defined [0.05, 0.95].

        Returns:
            bound_values: a list [p_a, p_b] containing values that bound a credible interval, such that a fraction cred_interval[0] of the posterior mass falls below p_a and a fraction cred_interval[1] falls below p_b.
        """
        posterior_array.sort()
        interval = []
        for interval_frac in self.cred_interval:
            interval.append(self._get_interval_val(posterior_array, interval_frac))
        return interval
        
        
    def _get_interval_val(self, array, fraction):
        """
        Returns the posterior value below which some fraction of posterior mass falls (could be the upper or lower bound of a credible interval).

        array: a posterior array or list
        fraction: fraction of posterior mass below the returned value
        """
        n_pts_below = int(round(fraction*(len(array))))
        return 0.5*(array[n_pts_below]+array[n_pts_below-1])


    def _get_highest_density_bounds(self, posterior_array, credibility):
        """
        Required input:
            posterior_array: a list or array of posterior values
            credibility: float between 0 and 1, denoting the credibility of the HDI.

        Returns:
            HDI: a list [p_a, p_b] containing the lower and upper value of the minimum width Bayesian credible interval
        """
        check_near_zero = 10
        posterior_array.sort()
        #Number of samples generated
        nSample = len(posterior_array)
        #Number of samples included in the HDI
        nSampleCred = int(math.ceil(nSample*credibility))
        #Number of intervals to be compared
        nCI = nSample - nSampleCred
        #Width of every proposed interval
        best_width = max(posterior_array)
        
        for i in range(nCI):
            if i == 0:
                width = posterior_array[i+nSampleCred-1] - posterior_array[i]
            else:
                width = posterior_array[i+nSampleCred-1] - posterior_array[i]
            if width<best_width:
                best_width = width
                best_index = i

        #Index of lower bound of shortest interval (the HDI)
        if (best_index == 0 and posterior_array[0]<posterior_array[check_near_zero]-posterior_array[0]):
            HDI = [0.0, posterior_array[best_index+nSampleCred]]
        else:
            HDI = [posterior_array[best_index], posterior_array[best_index+nSampleCred]]
        return HDI


    def _report_post_param_info(self, input_vals, posterior_arrays, calib_bounds, sums):
        """
        For a given run in a sensitivity analysis, for some posterior credibility, determines and optionally prints the posterior median and mean.
        Also optionally prints:
        - Credible bounds on all parameters
        - The parameter value inputted to the generator
        - The posterior window (width of the C.I.)
        """
        for param_name in posterior_arrays:
            b = calib_bounds[param_name]
            median = np.median(posterior_arrays[param_name])
            sums[param_name]['median'] += median
            mean = np.mean(posterior_arrays[param_name])
            sums[param_name]['mean'] += mean

            if len(self.cred_interval) == 1:
                logger.debug("{} < {}. Input: {}".format(param_name, b[0], input_vals[param_name]))
            elif len(self.cred_interval) == 2:
                sums[param_name]['lower'] += b[0]
                sums[param_name]['upper'] += b[1]
                logger.debug("{} < {} < {}, Median={}, Mean={}. Input value: {}. Window: {}".format(b[0], param_name, b[1], median, mean, input_vals[param_name], b[1]-b[0]))
            else:
                logger.info("Please input a list of either one or two bounds.")

    def _report_calibration_results(self, calib_bounds, consistent_with_zero, coverages, sums):
        """
        Prints coverages and summary interval information
        """
        for param_name in calib_bounds:
            #Optionally reporting how often each parameter is consistent with zero
            if self.check_if_nonzero == True:
                zero_frac = float(consistent_with_zero[param_name])/len(self.files)
                logger.info('{} CALIBRATION: {}% of inputted values are consistent with zero.'.format(param_name, zero_frac*100))
                
            #Printing coverages and summary interval information
            if len(self.cred_interval) == 1:
                logger.info('{}% of inputted {} values fell below a {}% posterior limit.'.format(coverages[param_name]*100, param_name, alpha*100))
                widths = [i[0] for i in calib_bounds[param_name]]
            elif len(self.cred_interval) == 2:
                logger.info('{} CALIBRATION: {}% of inputted values fell in a {}-{}% posterior interval.'.format(param_name, coverages[param_name]*100, self.cred_interval[0]*100, self.cred_interval[1]*100))
                avgs = {key:val/float(len(self.files)) for key, val in sums[param_name].items()}
                logger.info("{} AVERAGES: {} < {} < {}; Median val={}; Mean val={}".format(param_name, avgs['lower'], param_name, avgs['upper'], avgs['median'], avgs['mean']))
                widths = [i[1]-i[0] for i in calib_bounds[param_name]]
                
            logger.info("{} Mean interval width: {}; Median: {}".format(param_name, np.mean(widths), np.median(widths)))
            logger.info("{} Minumum width: {}; Maximum: {}\n--------------------------------------------------------".format(param_name, np.amin(widths), np.amax(widths)))

    def InternalRun(self):
        self.results = self.perform_calibration()
        return True

