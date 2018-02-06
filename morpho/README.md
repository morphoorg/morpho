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
 - ```resampling.py```: Resamples the content of a ROOT tree using a bootstrap randomization technique

See http://morpho.readthedocs.io/en/latest/better_apidoc_out/morpho.preprocessing.html.

plot
---------------
Plotting scripts use ROOT or R files to create plots of interest. After running Stan, we recommend using ```aposteriori_distribution``` to visualize posteriors and correlations of Stan parameters, and using ```histo2D_divergence``` to visualize the distribution of any divergent transitions.

 - ```histo.py```—Contains generic methods for plotting ROOT histograms (1D and 2D). A user may select the following methods in a configuration file:
   * ```histo```: Plots a 1D histogram using a list of data (```x```)
   * ```spectra```: Plots a 1D histogram using two lists of data (```x,bin_content```)
   * ```histo2D```: Plots a 2D histogram using two lists of data (```x,y```)
   * ```histo2D_divergence```: Plots a 2D histogram using two lists of data (```x,y```), and colors points with ```divergence==1``` differently from ```divergence==0```
   * ```aposteriori_distribution```: Plots a series of 2D histograms using a list of data names (>=3). It forms pairs of variables (```x,y```) and arranges the 2D histograms to get a view of the a posteriori distributions of these parameters.
   * ```correlation_factors```: Plots a grid in which color represents the correlation factor between each pair of variables.

 - ```neutrino_params.py```—An example of a processor specific to a particular analysis—in this case, one designed to extract posteriors of neutrino mass and mixing parameters. A user may select the following method:
   * ```neutrino_params```: Loads a Stan fit object from a pickle file, then invokes whichever plotting functions are indicated by the ```plotting_options: [opt1, opt2 ...]``` entry in the input configuration dictionary. That dictionary also contains keys ```output_path```, ```read_cache_name``` (file containing cache filename), ```input_fit_name``` (pickle file), ```data``` (containing Stan parameter names), and optionally, ```hierarchy``` (a specification of the neutrino mass hierarchy). Possible plotting options: ```_plot_neutrino_masses```, ```_plot_mass_params```, ```_plot_mixing_params```, and ```_plot_contours```.

 - ```plotting_routines.py```—Contains functions that may be useful for multiple plotting modules.
   * ```_uniquify```: Each time a file is created the with same filename (in the same directory), adds a consecutively higher number to the end of the filename.
   * ```_unpickle_with_cache```: Using a cache file, unpickles a pickle file to return a Stan fit object as well as a dictionary of Stan parameters and their posteriors (extracted from the fit).

 - ```spectra.py```—A method for visually comparing data inputted to a model with "predicted data" generated using posteriors extracted by fitting the model to the inputted data. Serves as a test of whether the model yields reasonable posteriors. This method needs to be updated and generalized. A user may select the following method:
   * ```spectra```: Loads a Stan fit object from a pickle file, then invokes whichever plotting functions are indicated by the ```plotting_options: [opt1, opt2 ...]``` entry in the input configuration dictionary. The ```overlay``` option allows for a data comparison.

 - ```timeseries.py```—Displays histograms with ROOT. Deprecated; to be removed.

 - ```countours.py```—Creates a matrix of contour/2D density plots for each combination of parameters in an analysis Stan model fit. Deprecated; to be removed.

See http://morpho.readthedocs.io/en/latest/better_apidoc_out/morpho.plot.html.


postprocessing
---------------


See http://morpho.readthedocs.io/en/latest/better_apidoc_out/morpho.postprocessing.html