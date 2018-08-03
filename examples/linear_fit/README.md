# Linear fit example

The ```linear_fit``` analysis serves as an example of how to use morpho, and specifically, how to prepare a configuration file, Stan model and data file for a morpho run. 
See [Instructions for Use: Before You Run Morpho](https://github.com/project8/morpho/tree/doc_README#instructions-for-use) for more details regarding analysis file organization.

Run ```linear_fit``` from the ```examples``` folder by executing:

```
morpho --config linear_fit/scripts/morpho_linear_fit.yaml
```

Equivalently, you can run the same example using the python API:
```
python linear_fit/scripts/pystan_test.py
```

## Model

The ```linear_fit/models``` folder contains two examples Stan models ```model_linear_generator.stan``` and ```model_linear_fit.stan```. 
The first model will generate a set of points normally distributed along a line.
The data are saved into a R file
The data points are extracted from the file, Stan code model inputs these data points and it extracts posteriors for the line's slope and y-intercept, as well as the variance of the normal distribution.
Convenience plots are then produced: a a posteriori distribution plot of the model parameters and the time series.

## Executing the example

The example exists in two forms:
- A yaml configuration file
- A python script

### Configuration File

The configuration file ```linear_fit/scripts/morpho_linear_fit.yaml``` specifies the processors that should be used, how they should be connected together, how they are individually configured and in which order they should be run.
The content of the file possesses 2 main structures:
- The `processors-toolbox` dictionary
- The processors `configurations`

#### ```Processors-toolbox``` Block

This block defines the processors to be used and assigns these a name.
It also provide the connections between processors (which variable of a processor will be set as variable of another processor) and defines the order in which the processors will be executed.

```
processors-toolbox:
  # Define the processors and their names
    processors:
        - type: morpho:PyStanSamplingProcessor
          name: generator
        - type: IORProcessor
          name: writer
        - type: IORProcessor
          name: reader
        - type: morpho:PyStanSamplingProcessor
          name: analyzer
        - type: APosterioriDistribution
          name: posterioriDistrib
        - type: TimeSeries
          name: timeSeries
  # Define in which order the processors should be run and how connections should be made
    connections:
        - signal: "generator:results"
          slot: "writer:data"
        - signal: "reader:data"
          slot: "analyzer:data"
        - signal: "analyzer:results"
          slot: "posterioriDistrib:data"
        - signal: "analyzer:results"
          slot: "timeSeries:data"
```

The block is composed of two structures:
- `processors` defines the processors to be used and their names.
The type defines which class/processor should be used.
For example, we will use `PyStanSamplingProcessor` from the `morpho` package.
It is possible to import classes/processors from other packages (for example [mermithid](https://github.com/project8/mermithid)) by setting using `type: mermithid:ProcessorX` instead of `type: morpho:ProcessorY`.
If no package is given (for example: `type: TimeSeries`), it will look for the default `morpho` package.
- 


#### Processors configurations

### Python script



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
 name: "linear_fit"
 model:
   file: "./linear_fit/models/morpho_linear_fit.stan"
   function_file: None
   cache: "./linear_fit/cache"
 data:
   files:
     - name: "./linear_fit/data/input.data"
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
   name: "./linear_fit/results/morpho_linear_fit"
   format: "root"
   tree: "linear_fit"
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
     input_file_name : "./linear_fit/results/morpho_linear_fit.root"
     input_tree: "linear_fit"
     output_path: ./linear_fit/results/
     data:
       - a
```

See [Morpho 1 Example Scripts](https://morpho.readthedocs.io/en/latest/morpho1examples.html) for more information regarding the ```plot``` block set-up for various plotting modules. Those Example Scripts contain analogous guidance for setting up ```preprocessing``` and ```postprocessing``` blocks.

