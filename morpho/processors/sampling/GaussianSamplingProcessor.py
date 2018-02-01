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
    Sampling processor that will generate a simple gaussian distribution (mean: 0, width: 1).
    Does not require input data nor model (as they are define in the class itself)
    '''
    def __init__(self, *args, **kwargs):
        return

    def Configure(self, input):
        print(self, input)
        self.iter = reader.read_param(input,'iter',2000)
        print(self.iter)

    def Run(self):
        from ROOT import TRandom3
        ran = TRandom3()
        data = []
        for i in range(self.iter):
            data.append(ran.Gaus(0,1))
        return {'values':data}

