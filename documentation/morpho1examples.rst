========================================
Morpho 1 Example Scripts
========================================

The following are example yaml scripts for important Preprocessing, Postprocessing, and Plot routines in Morpho 1. The format of the yaml script for other methods can be obtained from the documentation for that method.

Preprocessing
----------------

"do\_preprocessing : true" must be in the morpho dictionary. The dictionaries below should be placed in a "which\_pp" dictionary inside the "preprocessing" dictionary.

bootstrapping
~~~~~~~~~~~~~~~~

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
----------------

"do\_postprocessing : true" must be in the morpho dictionary. The dictionaries below should be placed in a "which\_pp" dictionary inside the "postprocessing" dictionary.

general\_data\_reducer
~~~~~~~~~~~~~~~~

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
----------------

"do\_plots : true" must be in the morpho dictionary. The dictionaries below should be placed in a "which_plot" dictionary inside the "plot" dictionary.

(placeholder)
~~~~~~~~~~~~~~~~

(description)
::
   - method_name: ""
     module_name: ""
