========================================
Preprocessing
========================================

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
