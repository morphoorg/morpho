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
        self.__name = name
        return

    def read_param(dictionary, node, default):
        data = dictionary
        xpath = node.split('.')
        try:
            for path in xpath:
                data = data[path]
        except Exception as exc:
            if default == 'required':
                err = """FATAL: Configuration parameter {0} required but not\
                provided in config file!
                """.format(node)
                logger.debug(err)
                raise exc
            else:
                data = default
        return data

    def Configure(self, params):
        '''
        This method will be called by nymph to configure the processor
        '''
        logger.error("Default Configure method: need to implement your own")
        raise

    def Run(self):
        '''
        This method will be called by nymph to run the processor
        '''
        logger.error("Default Run method: need to implement your own")
        raise 


