An Example of How to Use Morpho (```morpho_test```)
======

The ```morpho_test``` analysis serves as an example of how to use morpho, and specifically, how to prepare a configuration file, Stan model and data file for a morpho run. See [Instructions for Use: Before You Run Morpho](use-instructions) for more details regarding analysis file organization.

Run ```morpho_test``` from the ```examples``` folder by executing:

```
morpho --config morpho_test/scripts/morpho_linear_fit.yaml
```


Model
---------------
The ```morpho_test/models``` folder contains an example Stan model ```morpho_linear_fit.stan```. The Stan code models inputted data as points normally distributed around a line, and it extracts posteriors for the line's slope and y-intercept, as well as the variance of the normal distribution.


Data
--------------
The data that is analyzed in Stan is contained in the R file ```morpho_test/data/input.data```.


Configuration File
---------------
The configuration file ```morpho_test/scripts/morpho_linear_fit.yaml``` specifies that morpho will analyze the data in ```input.data``` using the Stan model ```morpho_linear_fit.stan```. In also tells morpho to output posteriors as well as convergence diagnostics to a root file and to create relevant plots. 

### The ```morpho``` Block ###
The user specifies which processors morpho will invoke. In this case, it will run the main Stan function and produce plots:

```
morpho:
  do_preprocessing: False
  do_stan: True
  do_postprocessing: False
  do_plots: True
```

### The ```stan``` Block ###
The user specifies Stan running conditions, input and output data files, and values of "data" parameters in the Stan code:

```
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
```

The ```model``` sub-block loads in the Stan model file and caches the compiled code. It is also possible to load in external functions located in separate files. The ```data``` sub-block reads in data from specified files and/or entries under ```parameters```. The ```run``` sub-block controls how Stan is run (choice of algorithm, number of chains, number of warmup transitions, total number of iterations, parameter initialization values). Finally, the ```output``` sub-block saves posteriors to a file.


### The ```plot``` Block ###

The user specifies which plotting processors and modules morpho should employ, as well as information specific to those modules:

```
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
```

See [Morpho 1 Example Scripts](https://morpho.readthedocs.io/en/latest/morpho1examples.html) for more information regarding the ```plot``` block set-up for various plotting modules. Those Example Scripts contain analogous guidance for setting up ```preprocessing``` and ```postprocessing``` blocks.

