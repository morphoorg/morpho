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
If really none of the existing classes is off any help for you, creating a new processor from scratch is the way to go.

Structure and requirements for a new processor
---------------------------------------



.. _tracker: https://github.com/morphoorg/morpho/issues
.. _Slack: https://morphoorg.slack.com/
.. _there: https://morpho.readthedocs.io/en/latest/morpho2framework.html#a-new-underlying-framework
