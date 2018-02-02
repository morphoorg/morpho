========================================
Postprocessing
========================================

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

