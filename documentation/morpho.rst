========================================
Morpho
========================================

  Morpho is a python interface to the Stan/PyStan Markov Chain Monte
  Carlo package.

  Morpho is intended as a meta-analysis tool to fit or generate data,
  organize inflow and outflow of data and models.

  For more information, also see:

  Stan:     http://mc-stan.org

  PyStan: https://pystan.readthedocs.io/en/latest/index.html

========================================
An Example File
========================================

Let us now take apart an example file to illustrate how morpho
functions.  You can find the example file in::
  morpho/examples/morpho_test/scripts/morpho_linear_fit.yaml

Let us start with the initiation portion of the configure file::
  morpho:
  do_preprocessing: False
  do_stan: True
  do_postprocessing: False
  do_plots: True


  
stan:
  # Name of the model
  name: "morpho_test"
  # Model, associated functions, cache folder
  model:
    file: "./morpho_test/models/morpho_linear_fit.stan"
    function_file: None
    cache: "./morpho_test/cache"
  # Input data
  data:
    files:
      - name: "./morpho_test/data/input.data"
        format: "R"
    parameters: 
      - N: 30
  # Run parameters
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

  # Output destination
  output:
    name: "./morpho_test/results/morpho_linear_fit"
    format: "root"
    tree: "morpho_test"
    inc_warmup: False
