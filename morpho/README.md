Morpho Processors
======

Morpho employs processor methods when directed to do so by a configuration file.


loader
---------------
The loader script ```pystanLoad.py``` imports root and hdf5 (depreciated) files for use by PyStan.

See <API link.?

preprocessing
---------------
Preprocessing scripts create new Stan inputs from loaded data.
 - resampling.py: Resamples the content of a ROOT tree using a bootstrap randomization technique

See <API link.>

plot
---------------
Plotting scripts use ROOT or R files to create plots of interest. After running Stan, we recommend using aposteriori_distribution to visualize posteriors/correlations of Stan parameters and histo2D_divergence to visualize the distribution of any divergent transitions.

 - histo.py: Contains generic methods to plot ROOT histograms (1D and 2D)
   List of methods:
   * histo: Plots a 1D histogram using a list of data (x)
   * spectra: Plots a 1D histogram using two lists of data (x,bin_content)
   * histo2D: Plots a 2D histogram using two lists of data (x,y)
   * histo2D_divergence: Plots a 2D histogram using two lists of data (x,y), and colors points with divergence==1 differently from divergence==0
   * aposteriori_distribution: Plots a series of 2D histograms using a list of data names (>=3). It forms pairs of variables (x,y) and arranges the 2D histograms to get a view of the aposteriori distributions of these parameters.
   * correlation_factors: Plots a grid in which color represents the correlation factor between each pair of variables.


See <API link.>

postprocessing
---------------
