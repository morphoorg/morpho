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

Let us start with the initiation portion of the configuration.
::
  morpho:
   do_preprocessing: False
   do_stan: True
   do_postprocessing: False
   do_plots: True
  
