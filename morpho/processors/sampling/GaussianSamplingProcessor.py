'''
Gaussian distribution sampling processor
'''

from __future__ import absolute_import

import json
import os

from morpho.utilities import morphologging, reader
from morpho.processors import BaseProcessor
logger=morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)

class GaussianSamplingProcessor(BaseProcessor):
    '''
    Sampling processor that will generate a simple gaussian distribution.
    Does not require input data nor model (as they are define in the class itself)
    '''

    def _Configure(self, input):
        self.iter = int(reader.read_param(input,'iter',2000))
        self.mean = reader.read_param(input,"mean",0.)
        self.width = reader.read_param(input,"width",1.)
        if self.width<=0.:
            raise ValueError("Width is negative or null!")

    def _Run(self):
        from ROOT import TRandom3
        ran = TRandom3()
        data = []
        for i in range(self.iter):
            data.append(ran.Gaus(self.mean,self.width))
        return {'x':data}

