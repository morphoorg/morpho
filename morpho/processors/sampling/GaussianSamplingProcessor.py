'''
Gaussian distribution sampling processor
Authors: M. Guigue
Date: 06/26/18
'''

from __future__ import absolute_import

from morpho.utilities import morphologging, reader
from morpho.processors import BaseProcessor
logger = morphologging.getLogger(__name__)


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
