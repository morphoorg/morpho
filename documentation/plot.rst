========================================
Plots
========================================

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

1)  Plotting contours, densities, and matricies (often to look for correlations).
  
2)  Time series to study convergences.


