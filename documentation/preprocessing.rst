========================================
Preprocessing
========================================

Preprocessing functions are applied to data in advance of executing
the fitter.  Typically this is done to prepare the data in some state
in advance of fitting.

Available Functions
======


Bootstrapping(param_dict)
------------------

  Resample the content of a tree usng a bootstrap technique (some
  samples can be used twice).

  Inputs:
  -----
  input_file_name :  Name of root file name to read in
  
  input_tree:  Name of root tree

  number_data:  Number of iterations to sample
  
  Outputs:
  -----
  output_file_name :  Name of root file name to read in 
                                 (uses input_file_name if not
				 specified)
				 
  output_tree:  Name of root tree for output
                                   (uses input_tree if not specified)

  

  
