========================================
Morpho 1
========================================

Introduction
------------------

Morpho is a python interface to the Stan/PyStan Markov Chain Monte
Carlo package.

Morpho is intended as a meta-analysis tool to fit or generate data,
organize inflow and outflow of data and models.

For more information, also see:

Stan:     http://mc-stan.org

PyStan: https://pystan.readthedocs.io/en/latest/index.html

Install
------------------

Dependencies
'''''''''''''

The following dependencies should be installed (via a package manager) before installing morpho:

  * python (2.7.x; 3.x not supported)
  * python-pip
  * git
  * python-matplotlib

  Morpho reads and saves files in either **R** or **ROOT.** If you would like to use root, install root-system or see https://root.cern (and ensure that the same version of python is enabled for morpho and ROOT).

Virtual environment-based installation
'''''''''''''''''''''''''''''''''''''''

We recommend installing morpho using pip inside a python virtual environment. Doing so will automatically install dependencies beyond the four listed above, including PyStan 2.15.

If necessary, install [virtualenv](https://virtualenv.pypa.io/en/stable/), then execute::

  virtualenv ~/path/to/the/virtualenvironment
  source ~/path/to/the/virtualenvironment/bin/activate #Activate the environment
  #Use "bash deactivate" to exit the environment
  pip install -U pip #Update pip to >= 7.0.0
  cd ~/path/to/morpho
  pip install .
  pip install .[all]

Docker installation
''''''''''''''''''''

If you would like to modify your local installation of morpho (to add features or resolve any bugs), we recommend you use a [Docker container](https://docs.docker.com/get-started/) instead of a python virtual environment. To do so:

  1. Install Docker: https://docs.docker.com/engine/installation/.
  2. Clone and pull the latest master version of morpho.
  3. Inside the morpho folder, execute ``docker-compose run morpho``. A new terminal prompter (for example, ``root@413ab10d7a8f:``) should appear.
     You may make changes to morpho either inside or outside of the Docker container. If you wish to work outside of the container, move morpho to the ``morpho_share`` directory that is mounted under the ``/host`` folder created by docker-compose.
  4. You can remove the container image using ``docker rmi morpho_morpho``.

If you develop new features or identify bugs, please open a GitHub issue.

Running Morpho
------------------

Once the relevant data, model and configuration files are at your disposal, run morpho by executing::

 morpho --config  /path/to/json_or_yaml_config_file --other_options


You can test morpho using the example in the morpho_test directory::

   morpho --config morpho_test/scripts/morpho_linear_fit.yaml


An Example File
------------------

The format allows the user to execute Stan using standarized scripts.
Let us now take apart an example file to illustrate how morpho
functions.  You can find the example file in
::

    morpho/examples/morpho_test/scripts/morpho_linear_fit.yaml

Let us start with the initiation portion of the configuration.
::

  morpho:
   do_preprocessing: False
   do_stan: True
   do_postprocessing: False
   do_plots: True
  
Under the morpho block, you can select how the processors will be
run.  In this case, it will run the main Stan function and produce
plots at the end of processing.

Next, we come to the main Stan configuration block, where both running
conditions, data and parameters can be fed into the Stan model.
::

   stan:
   name: "morpho_test"
   model:
      file: "./morpho_test/models/morpho_linear_fit.stan"
      function_file: None
      cache: "./morpho_test/cache"
    data:
      files:
      - name: "./morpho_test/data/input.data"
         format: "R"
      parameters: 
       - N: 30
    run:
      algorithm: "NUTS"
      iter: 4000
      warmup: 1000
      chain: 12
      n_jobs: 2
      init:
       - slope : 2.0
         intercept : 1.0
         sigma: 1.0
    output:
      name: "./morpho_test/results/morpho_linear_fit"
      format: "root"
      tree: "morpho_test"
      inc_warmup: False
      branches:
      - variable: "slope"
        root_alias: "a"
      - variable: "intercept"
        root_alias: "b"

The model block allows you to load in your Stan model file (for more
on Stan models, see PyStan or Stan documentations).  The compiled code
can be cached to reduce running time.  It is also possible to load in
*external*  functions located in separated files elsewhere.

The next block, the data block, reads in data.  File formats include
R and root.  One can also load in parameters directly using the
parameters block, as we do for the variable *N*.

The next block, the run block, allows one to control how Stan is run
(number of chains, warmup, algorithms, etc.).  Initializations can
also be set here.  This block feeds directly into PyStan.

The last block within the Stan block is the output.  In this example,
we save to a root file, and maintain two variables, *a* and *b*.

Since we specified the configure file to also make some plots, we can
set up those conditions as well.  In our example again, we have::

  plot:
   which_plot:
    - method_name: histo
      module_name: histo
      title: "histo"
      input_file_name : "./morpho_test/results/morpho_linear_fit.root"
      input_tree: "morpho_test"
      output_path: ./morpho_test/results/
      data:
        - a

The plot saves a PDF of the variable *a* based on the root file
results.

The flow is thus as follows.  Morpho is told to execute Stan and its
plotting features.  The Stan execution reads in external data and sets
the running in much the same way as PyStan does.  Results are then
saved to the results folder (in this case, under root files).  Plots
are also executed to ensure the quality of results.

Preprocessing
------------------

Preprocessing functions are applied to data in advance of executing
the fitter.  Typically this is done to prepare the data in some state
in advance of fitting.

Preprocessing can be set as a flag in the beginning of the
configuration file.  As an example
::

   morpho:
     do_preprocessing: true

Later in the configuration file, you can set up the commands to
pre-process data
::

   preprocessing:
    which_pp:
     - method_name: bootstrapping
       module_name: resampling
       input_file_name: ./my_spectrum.root
       input_tree: input
       output_file_name: ./my_fit_data.root
       output_tree: bootstrapped_data
       option: "RECREATE"
       number_data: 5000


In the above example, it will randomly sample 5000 data points from
the root file "my_spectrum.root" (with tree input) and save it to a
new data file called "./my_fit_data.root" with tree name "
bootstrapped_data".

Postprocessing
------------------

Postprocessing functions are applied to data after executing
the fitter.  Typically this is done examine the parameter information and check for convergence.

Postprocessing can be set as a flag in the beginning of the
configuration file.  As an example
::

   morpho:
     do_postprocessing: true

Later in the configuration file, you can set up the commands to
post-process data.  For example, to reduce the data into bins
::

   preprocessing:
    which_pp:
     - method_name: general_data_reducer
       module_name: general_data_reducer
       input_file_name: ./my_spectrum.root
       input_file_format: root
       input_tree: spectrum
       data:
        -Kinetic_Energy
       minX:
        -18500.
       maxX:
        -18600.
       nBinHisto:
        -1000
       output_file_name: ./my_binned_data.root
       output_file_format: root
       output_tree: bootstrapped_data
       option: "RECREATE"

In the above example, it will take data from the root file saved in the *Kinetic_Energy* parameter and rebin it in a 1000-bin histogram.

Plots
------------------

Plotting is a useful set of routines to make quick plots and
diagnostic tests, usualluy after the Stan main executable has been run.::

   morpho:
     do_plots: true

Later in the configuration file, you can set up the commands to
plot data after the fitter is complete.
::

   plot:
   which_plot:
    - method_name: histo
       title: "histo"
       input_file_name : "./morpho_test/results/morpho_linear_fit.root"
       input_tree: "morpho_test"
       output_path: ./morpho_test/results/
       data:
        - a

In the above example, it will take data from the root file saved in
the *a* parameter plot and save it to ./morpho_test/results/histo_a.pdf

We have plotting schemes that cover a number of functions:

1.  Plotting contours, densities, and matricies (often to look for correlations).
2.  Time series to study convergences.

Example Script
------------------
The following are example yaml scripts for important Preprocessing, Postprocessing, and Plot routines in Morpho 1. The format of the yaml script for other methods can be obtained from the documentation for that method.

Preprocessing
'''''''''''''

"do\_preprocessing : true" must be in the morpho dictionary. The dictionaries below should be placed in a "which\_pp" dictionary inside the "preprocessing" dictionary.


bootstrapping
'''''''''''''

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
'''''''''''''''

"do\_postprocessing : true" must be in the morpho dictionary. The dictionaries below should be placed in a "which\_pp" dictionary inside the "postprocessing" dictionary.

general\_data\_reducer
'''''''''''''''''''''''

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
''''

"do\_plots : true" must be in the morpho dictionary. The dictionaries below should be placed in a "which_plot" dictionary inside the "plot" dictionary.

contours
''''''''''

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
'''''''

Plot a 1D histogram using a list of data
::

  - method_name: "histo"
    module_name: "histo"

spectra
''''''''

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
''''''''''

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
'''''''''''''''''''

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
'''''''''''''''''''''''''''

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
'''''''''''''''''''''

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
