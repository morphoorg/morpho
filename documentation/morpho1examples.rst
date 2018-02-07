========================================
Morpho 1 Example Scripts
========================================

The following are example yaml scripts for important Preprocessing, Postprocessing, and Plot routines in Morpho 1. The format of the yaml script for other methods can be obtained from the documentation for that method.

Preprocessing
----------------

"do\_preprocessing : true" must be in the morpho dictionary. The dictionaries below should be placed in a "which\_pp" dictionary inside the "preprocessing" dictionary.

bootstrapping
~~~~~~~~~~~~~~~~

The bootstrapping method resamples the contents of a tree. Instead of regenerating a fake data set on every sampler, one can generate a larger data set, then extract s
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

(placeholder)
~~~~~~~~~~~~~~~~

(description)
::
     - method_name: ""
       module_name: ""

Plot
----------------

"do\_plots : true" must be in the morpho dictionary. The dictionaries below should be placed in a "which_plot" dictionary inside the "plot" dictionary.

(placeholder)
~~~~~~~~~~~~~~~~

(description)
::
   - method_name: ""
     module_name: ""
