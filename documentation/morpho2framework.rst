-------------------------
Morpho 2: a new framework
-------------------------

Morpho is an analysis framework based on the Stan/PyStan Markov Chain Monte
Carlo package and the ROOT/RooFit C++ library.

Similarly to Morpho 1, Morpho 2 is intended as a meta-analysis tool to fit or generate data,
organize inflow and outflow of data and models.

A new underlying framework
--------------------------

Morpho 2 uses a framework similar to `Nymph`_: it uses classes called `processors` to act on the data.
All classes inherites from a `BaseProcessor` class where all the common behaviors are encoded.
However the exchange of informations between processors is less constraint than the `Katydid`_ implementation of Nymph.
The `output` of a processor is contained into an internal variable of the processor, and is generally a dictionary.

The connection between processors is usually defined into a configuration file, but can be done `manually` using the morpho python API.
An example of both implementation can be found here :ref:`morpho2-example-label`.

.. _`Nymph`: https://github.com/project8/nymph
.. _`Katydid`: https://github.com/project8/katydid


An extensible module
--------------------

Morpho is intended to be a generic analysis framework.
It contains processors that users can find useful, regardless of their field.
Suggestions of new processors and features are welcome and can be submitted via issue posting on Github.

When processors are needed by users for a specific processor (e.g. a processor that reads files with a specific formatting), it is recommended to set these into an `extension`.
Extensions would then contain all the processors and be installed along with morpho and used via the main `morpho` executable which would look for the needed processors.

An example of such extension is `mermithid`_: it contains processors related to the file formatting needed by the Project 8 collaboration.
It also implements RootFit sampling and fitting processors that makes use of custom beta decay spectrum shapes.
The associated pdf are compiled (via `CMake`_) and the libraries appended to the `PYTHONPATH` before the installation of the module
Finally a plotting processor (generating Kurie plots) specific to this experiment is kept there.

.. _`mermithid`: https://github.com/project8/mermithid
.. _`CMake`: https://cmake.org

An interface with external software
-----------------------------------

Thanks to this new framework and the extensitvity of the package, it is easy to interface with other softwares.
Several ways of implementing such interfacing are possible and should be implemented depending on how complex the interfacing is:

1. If the new piece of code is contain into a simple function into a python script, one can use as a first step the ProcessorAssistant to wrap the function into a processor (this does require the creation of an extension). Eventually, for production usage, a new processor with the desired behavior should be created (this might require the creation of an extension).
2. If morpho needs to interface with an external library (e.g. some C++ code), an extension is highly recommended. The libraries can be built before the installation of the extension. An example of such implementation is `mermithid`_.
