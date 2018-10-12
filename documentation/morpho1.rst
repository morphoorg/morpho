========================================
Morpho 1: Introduction
========================================

Morpho is a python interface to the Stan/PyStan Markov Chain Monte
Carlo package.

Morpho is intended as a meta-analysis tool to fit or generate data,
organize inflow and outflow of data and models.

For more information, also see:

Stan:     http://mc-stan.org

PyStan: https://pystan.readthedocs.io/en/latest/index.html


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

