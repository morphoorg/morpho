========================================
Morpho 1: Example Scripts
========================================

The following are example yaml scripts for important Preprocessing, Postprocessing, and Plot routines in Morpho 1. The format of the yaml script for other methods can be obtained from the documentation for that method.

Preprocessing
-------------

"do\_preprocessing : true" must be in the morpho dictionary. The dictionaries below should be placed in a "which\_pp" dictionary inside the "preprocessing" dictionary.

bootstrapping
~~~~~~~~~~~~~

Resamples the contents of a tree. Instead of regenerating a fake data set on every sampler, one can generate a larger data set, then extract subsets.
::

   - method_name: "boot_strapping"
     module_name: "resampling"
     input_file_name: "input.root" # Name of file to access
                                   # Must be a root file
     input_tree: "tree_name" # Name of tree to access
     output_file_name: "output.root" # Name of the output file
                                     # The default is the same the input_file_name
     output_tree: "tree_name" # Tree output name
                              # Default is same as input.
     number_data: int # Number of sub-samples the user wishes to extract.
     option: "RECREATE" # Option for saving root file (default = RECREATE)

Postprocessing
--------------

"do\_postprocessing : true" must be in the morpho dictionary. The dictionaries below should be placed in a "which\_pp" dictionary inside the "postprocessing" dictionary.

general\_data\_reducer
~~~~~~~~~~~~~~~~~~~~~~

Tranform a function defining a spectrum into a histogram of binned data points.
::
  - method_name: "general_data_reducer"
    module_name: "general_data_reducer"
    input_file_name: "input.root" # Path to the root file that contains the raw data
    input_file_format: "root" # Format of the input file
                              # Currently only root is supported
    input_tree: "spectrum" #  Name of the root tree containing data of interest
    data: ["KE"] # Optional list of names of branches of the data to be binned
    minX:[18500.] # Optional list of minimum x axis values of the data to be binned
    maxX:[18600.] # Optional list of maximum x axis values of the data to be binned
    nBinHisto:[50] # List of desired number of bins in each histogram
    output_file_name: "out.root", # Path to the file where the binned data will be saved
    output_file_format: "root", # Format of the output file
    output_file_option: RECREATE # RECREATE will erase and recreate the output file
                                 # UPDATE will open a file (after creating it, if it does not exist) and update the file.

Plot
----

"do\_plots : true" must be in the morpho dictionary. The dictionaries below should be placed in a "which_plot" dictionary inside the "plot" dictionary.

contours
~~~~~~~~~~~~~~~~

contours creates a matrix of contour plots using a stanfit object
::

  - method_name: "contours"
    module_name: "contours"
    read_cache_name: "cache_name_file.txt" # File containing path to stan model cache
    input_fit_name: "analysis_fit.pkl"# pickle file containing stan fit object
    output_path: "./results/" # Directory to save results in
    result_names: ["param1", "param2", "param3"] # Names of parameters to plot
    output_format: "pdf"

histo
~~~~~~~~~~~~~~~~

Plot a 1D histogram using a list of data
::

  - method_name: "histo"
    module_name: "histo"

spectra
~~~~~~~~~~~~~~~~

Plot a 1D histogram using 2 lists of data giving an x point and the corresponding bin contents
::

  - method_name: "spectra"
    module_name: "histo"
    title: "histo"
    input_file_name : "input.root"
    input_tree: "tree_name"
    output_path: "output.root"
    data:
        - param_name

histo2D
~~~~~~~~~~~~~~~~

Plot a 2D histogram using 2 lists of data
::

  - method_name: "histo2D"
    module_name: "histo"
    input_file_name : "input.root"
    input_tree: "tree_name"
    root_plot_option: "contz"
    data:
      - list_x_branch
      - list_y_branch

histo2D_divergence
~~~~~~~~~~~~~~~~~~

Plot a 2D histogram with divergence indicated by point color
::

  - method_name: "histo2D_divergence"
    module_name: "histo"
    input_file_name : "input.root"
    input_tree: "tree_name"
    root_plot_option: "contz"
    data:
      - list_x_branch
      - list_y_branch

aposteriori_distribution
~~~~~~~~~~~~~~~~~~~~~~~~

Plot a grid of 2D histograms
::

  - method_name: "aposteriori_distribution"
    module_name: "histo"
    input_file_name : "input.root"
    input_tree: "tree_name"
    root_plot_option: "cont"
    output_path: output.root
    title: "aposteriori_plots"
    output_format: pdf
    output_width: 12000
    output_height: 1100
    data:
      - param1
      - param2
      - param3

correlation_factors
~~~~~~~~~~~~~~~~~~~

Plot a grid of correlation factors
::

  - method_name: "correlation_factors"
    module_name: "histo"
    input_file_name : "input.root"
    input_tree: "tree_name"
    root_plot_option: "cont"
    output_path: output.root
    title: "aposteriori_plots"
    output_format: pdf
    output_width: 12000
    output_height: 1100
    data:
      - param1
      - param2
      - param3
