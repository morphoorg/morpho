'''
Base processor for sampling-type operations
'''

from __future__ import absolute_import

import json
import os

from morpho.utilities import morphologging
logger=morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)

class BaseProcessor:
    '''
    Base Processor
    All Processors will be implemented in a child class where the 
    specifics are encoded by overwriting Configure and Run.
    '''

    def __init__(self, name, *args, **kwargs):
        self._procName = name
    
    @property
    def name(self):
        return self._procName

    def Configure(self, params):
        '''
        This method will be called by nymph to configure the processor
        '''
        logger.info("Configure <{}> with {}".format(self.name,params))
        self._Configure(params)

    def _Configure(self, params):
        logger.error("Default _Configure method: need to implement your own")
        raise

    def Run(self):
        '''
        This method will be called by nymph to run the processor
        '''
        logger.info("Run <{}>...".format(self.name))
        result = self._Run()
        logger.info("Done with <{}>".format(self.name))
        return result
    
    def _Run(self):
        logger.error("Default Run method: need to implement your own")
        raise 


