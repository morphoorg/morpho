Morpho Processors
======

Morpho employs processor methods when directed to do so by a configuration file.

Processors are executed in the following order:
loader &rarr; preprocessing &rarr; [Stan] &rarr; plot &rarr; postprocessing.


loader
---------------
The loader script ```pystanLoad.py``` imports root and hdf5 (deprecated) files for use by PyStan.

See http://morpho.readthedocs.io/en/latest/better_apidoc_out/morpho.loader.html.

preprocessing
---------------
Preprocessing scripts create new Stan inputs from loaded data.
 - ```resampling.py```: One may wish to perform an analysis on many similar sets of pseudo-data. To forestall the need to generate data repeatedly, ```resampling.py``` reads data from a ROOT tree, and either a) creates a slightly larger data set using the original set, then extracts a subset (bootstrapping randomization) or b) randomly selects a subset from the original set (JackKnife randomization).

See http://morpho.readthedocs.io/en/latest/better_apidoc_out/morpho.preprocessing.html.

plot
---------------
Plotting scripts use ROOT or R files to create plots of interest. After running Stan, we recommend using ```aposteriori_distribution``` to visualize posteriors and correlations of Stan parameters, and using ```histo2D_divergence``` to visualize the distribution(s) of any divergent transitions.

 - ```histo.py```—Contains generic methods for plotting ROOT histograms (1D and 2D). A user may select one or more of the following methods in the configuration file:
   * ```histo```: Plots a 1D histogram using a list of data (```x```).
   * ```spectra```: Plots a 1D histogram using two lists of data (```x,bin_content```).
   * ```histo2D```: Plots a 2D histogram using two lists of data (```x,y```).
   * ```histo2D_divergence```: Plots a 2D histogram using two lists of data (```x,y```), and colors points with ```divergence==1``` differently from points with ```divergence==0```.
   * ```aposteriori_distribution```: Plots a series of 2D histograms using a list of at least three data names. The method forms pairs of variables (```x,y```) and arrange 2D histograms to enable clear visualization of the a posteriori distributions of these parameters.
   * ```correlation_factors```: Plots a grid in which color represents the correlation factor between each pair of variables.

 - ```neutrino_params.py```—An example of a processor specific to a particular analysis—in this case, one designed to extract posteriors of neutrino mass-related parameters. A user may include the following method in the configuration file:
   * ```neutrino_params```: Loads a Stan fit object from a pickle file, then invokes whichever plotting functions are indicated by the ```plotting_options: [opt1, opt2 ...]``` entry in the input configuration dictionary. That dictionary also contains keys ```output_path```, ```read_cache_name``` (file containing cache filename), ```input_fit_name``` (pickle file), ```data``` (containing Stan parameter names), and optionally, ```hierarchy``` (a specification of the neutrino mass hierarchy). Possible plotting options: ```_plot_neutrino_masses```, ```_plot_mass_params```, ```_plot_mixing_params```, and ```_plot_contours```.

 - ```plotting_routines.py```—Contains functions that may be useful for multiple plotting modules.
   * ```_uniquify```: Each time a file is created the with same filename (in the same directory), adds a consecutively higher number to the end of the filename.
   * ```_unpickle_with_cache```: Using a cache file, unpickles a pickle file to return a Stan fit object as well as a dictionary of Stan parameters and their posteriors (extracted from the fit).

 - ```spectra.py```—Plot beta decay spectra, by calculating a spectral shape given a set of fixed input parameters and/or by scatter plotting (KE, spectrum) points from posterior distributions. This method needs to be updated and generalized to provide a visual comparison of data inputted to a model with "predicted data" generated using posteriors that were extracted by fitting to the inputted data. (This would serve as a test of whether the model yields reasonable posteriors.) A user may include the following method:
   * ```spectra```: Loads a Stan fit object from a pickle file, then invokes whichever plotting functions are indicated by the ```plotting_options: [opt1, opt2 ...]``` entry in the input configuration dictionary. The ```overlay``` option allows for a comparison of the fixed parameter spectrum and the scatter plot spectrum.

 - ```timeseries.py```—Displays histograms with ROOT. Deprecated; to be removed.

 - ```countours.py```—Creates a matrix of posterior contour/2D density plots for each combination of parameters in a Stan model. Deprecated; to be removed.

See http://morpho.readthedocs.io/en/latest/better_apidoc_out/morpho.plot.html.


postprocessing
---------------
Postprocessing scripts either create new outputs using the results of a Stan analysis or provide relevant information based on those results.

 - ```data_reducer.py```—Bins spectral data from a ROOT file. Deprecated; to be removed.
 
 - ```general_data_reducer.py```—Bins data points (creates a histogram) and saves the result to a ROOT output file. A user may include the following method in the configuration file:
   * ```general_data_reducer```: Creates and saves a histogram from one data array.
  
 - ```stan_utility.py```—Contains modules that perform quick diagnostic tests and that facilitate plotting designed to help diagnose whether the model has converged. Adapted from Michael Betancourt's script at https://github.com/betanalpha/jupyter_case_studies/blob/master/pystan_workflow/stan_utility.py.
   * ```check_all_diagnostics```: This is called automatically whenever Stan runs, and it prints quick checks of five convergence diagnostics to the screen. If any of checks indicate a failure to converge, the user should investigate the source of the problem. For help interpreting the diagnostics, see [Betancourt's "Robust Statistical Workflow with PyStan."](http://mc-stan.org/users/documentation/case-studies/pystan_workflow.html)
   * ```partition_div```: Returns Stan parameter arrays separated into divergent and non-divergent transitions. We intend to employ this function to help create plots like those currently produced by ```histo2D_divergence``` (see above).

See http://morpho.readthedocs.io/en/latest/better_apidoc_out/morpho.postprocessing.html.