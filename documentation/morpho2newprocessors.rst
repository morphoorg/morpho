---------------------------------------
How to create new processors
---------------------------------------

At that point you might be thinking that morpho is great, but it does not have the feature or a processor you want.
Before going any further, you should go in the morpho issue `tracker`_ to see if someone else is not working on this feature.
If you see something similar there, you should say so there and/or on the morphoorg `Slack`_.
If you don't, then you are in the right place to know how to create your own processor.

Generalities about processors
---------------------------------------

As you might have read `there`_, processors are objects that act on data and produce an output.
Generally processors actions are intended to be simple in order to keep things as modular as possible.
For example, you would prefer a processor that reads a file and one that acts on these compared with one that does both of these at once.

Morpho already provides a set of processors that could serve as a basis for your new processor.
For example, there exists a input/output base class that defines base methods for any processor reading/writing a specific file format.
If that is the case, you should consider using this class as a base class for your own.
If there is not such class but one could with some modifications, you should consider the possibility of doing these modifications so you could use this class as a base for your new processor.
If really none of the existing classes is of any help for you, creating a new processor from scratch is the way to go.

Structure and requirements for a new processor
---------------------------------------

Let's have a look at a basic example: the `GaussianSamplingProcessor`_. ::

        from morpho.utilities import morphologging, reader
        from morpho.processors import BaseProcessor
        logger = morphologging.getLogger(__name__)
        
        __all__ = []
        __all__.append(__name__)
        
        
        class GaussianSamplingProcessor(BaseProcessor):
                '''
                Sampling processor that will generate a simple gaussian distribution
                using TRandom3.
                Does not require input data nor model (as they are define in the class itself)
                Parameters:
                        iter (required): total number of iterations (warmup and sampling)
                        mean: mean of the gaussian (default=0)
                        width: width of the gaussian (default=0)
                Input:
                        None
                Results:
                        results: dictionary containing the result of the sampling of the parameters of interest
                '''

                def InternalConfigure(self, input):
                        self.iter = int(reader.read_param(input, 'iter', "required"))
                        self.mean = reader.read_param(input, "mean", 0.)
                        self.width = reader.read_param(input, "width", 1.)
                        if self.width <= 0.:
                                raise ValueError("Width is negative or null!")
                        return True
                
                def InternalRun(self):
                        from ROOT import TRandom3
                        ran = TRandom3()
                        data = []
                        for _ in range(self.iter):
                                data.append(ran.Gaus(self.mean, self.width))
                        self.results = {'x': data}
                        return True
                        
This processor aims at generating random values following a normal distribution using ``TRandom3`` from ROOT.
Processors all inherite from the BaseProcessor class that defines very basic behaviors.
BaseProcessor defines two methods ``InternalConfigure`` and ``InternalRun``.
``InternalConfigure`` is used to configure the processor: here the number of values to generate (``iter``), the mean (``mean``) and the width (``width``) are given to the processor from the configuration dictionary (this dictionary is extracted from the configuration file). This method makes sure that all the given parameters are okay so the execution will work fine: for example we make sure the width is positive.
``InternalRun`` is used for the actual execution: it produces the samples from the normal distribution.
The result of this sampling is saved inside a membre variable of the class (``results`` in this case) in the shape of a dictionary.
Contrary to Katydid, there are no defined data class defined in this framework for containing the intermediate results. 
We use python defined objects such as float, string, list or dictionary: we try to avoid using objects defined by external packages (such as ROOT or PyStan). 


.. _GaussianSamplingProcessor: https://github.com/morphoorg/morpho/blob/master/morpho/processors/sampling/GaussianSamplingProcessor.py
.. _tracker: https://github.com/morphoorg/morpho/issues
.. _Slack: https://morphoorg.slack.com/
.. _there: https://morpho.readthedocs.io/en/latest/morpho2framework.html#a-new-underlying-framework
