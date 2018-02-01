File Edit Options Buffers Tools Python Help
'''                                                                                                                                    
Creates Stan diagnostic plots in python.                                                                                               '''

from __future__ import absolute_import

import json
import os

from morpho.utilities import morphologging, reader
from morpho.processors import SamplingBaseProcessor
logger=morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)

class StanDiagnosticsPy(SamplingBaseProcessor):
    '''                                                                                                                               
    Creates plot displaying divergences. Should be expanded to create other diagnostic plots. Unfinished and untested.
                                                                                                                    
    '''
    def __init__(self, *args, **kwargs):
        return

    def Configure(self, params):
        self.data = params["data"]
        self.div_params = params["div_params"] #List containing lists of pairs of params to be used in creating divergence plots.
        # For example: [["mass", "Q"], ["Q," "sigma"]]

    def Run(self):
        light="#DCBCBC"
        light_highlight="#C79999"
        mid="#B97C7C"
        mid_highlight="#A25050"
        dark="#8F2727"
        dark_highlight="#7C0000"
        green="#00FF00"
        
        for xy_pair in self.div_params:

    def _partition_div(param_dict):
        """ Returns parameter arrays separated into divergent and non-divergent transitions"""
        
        import pystan
        import numpy

        div = numpy.concatenate([x['divergent__'] for x in sampler_params]).astype('int')
        params = _shaped_ordered_params(fit)
        nondiv_params = dict((key, params[key][div == 0]) for key in params)
        div_params = dict((key, params[key][div == 1]) for key in params)
        return nondiv_params, div_params
                                                                                
