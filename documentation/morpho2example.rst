----------------
Morpho 2 example
----------------

The ```linear_fit``` analysis serves as an example of how to use morpho, and specifically, how to prepare a configuration file, Stan model and data file for a morpho run.
See [Instructions for Use: Before You Run Morpho](https://github.com/project8/morpho/tree/doc_README#instructions-for-use) for more details regarding analysis file organization.

Run ```linear_fit``` from the ```examples``` folder by executing:
::
  morpho --config linear_fit/scripts/morpho_linear_fit.yaml


Equivalently, you can run the same example using the python API:
::
  python linear_fit/scripts/pystan_test.py


Model
-----

The ```linear_fit/models``` folder contains two examples Stan models ```model_linear_generator.stan``` and ```model_linear_fit.stan```.
The first model will generate a set of points normally distributed along a line.
The data are saved into a R file
The data points are extracted from the file, Stan code model inputs these data points and it extracts posteriors for the line's slope and y-intercept, as well as the variance of the normal distribution.
Convenience plots are then produced: a a posteriori distribution plot of the model parameters and the time series.

Executing the example
---------------------

The example exists in two forms:

- A yaml configuration file
- A python script

Configuration File
''''''''''''''''''''

The configuration file ```linear_fit/scripts/morpho_linear_fit.yaml``` specifies the processors that should be used, how they should be connected together, how they are individually configured and in which order they should be run.
The content of the file possesses 2 main structures:

- The `processors-toolbox` dictionary
- The processors `configurations`

The structure of the configuration file is very similar to the [Katydid](https://github.com/project8/katydid) software.

```Processors-toolbox``` Block
''''''''''''''''''''

This block defines the processors to be used and assigns these a name.
It also provide the connections between processors (which variable of a processor will be set as variable of another processor) and defines the order in which the processors will be executed.
::
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

The block is composed of two structures:

- `processors` defines the processors to be used and their names. The type defines which class/processor should be used. For example, we will use `PyStanSamplingProcessor` from the `morpho` package. It is possible to import classes/processors from other packages (for example [mermithid](https://github.com/project8/mermithid)) by setting using `type: mermithid:ProcessorX` instead of `type: morpho:ProcessorY`. If no package is given (for example: `type: TimeSeries`), it will look for the default `morpho` package.
- `connections` defines the order in which the processors are run. In the example, it will be `generator -> writer -> reader -> analyzer -> posterioriDistrib -> timeSeries`. It also defines how processors are connected together: for example the internal variable `results` of  `generator` (called *signal*) containing the MC samples as a dictionary will be given to `writer` as `data` (called *slot*). It is important that the signal and slot types match.

Processors configurations
''''''''''''''''''''

The following dictionaries defines the properties of each processor:
::
  # Configure generator
  generator:
    model_code: "linear_fit/models/model_linear_generator.stan"
    input_data:
        slope: 1
        intercept: -2
        xmin: 1
        xmax: 10
        sigma: 1.6
    iter: 530
    warmup: 500
    interestParams: ['x','y','residual']
    delete: False

Documentation about each processor parameters can be found in the source code in each class.

Python script
------------

Similarly it is possible to create, configure and run processors using the morpho python API.
An example can be found in `linear_fit/scripts/pystan_test.py`.
This example should do the exact same thing as the script above.

The python API is an alternative way of using morpho.
It can be used when the object must be modified between two processors and this cannot be done using a processor (or the ProcessorAssistant).
It is also useful to test new features.
However it is not the recommended method for production analyses.
