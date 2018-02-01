'''
Base input/output processor for reading and writing operations
'''

from __future__ import absolute_import

import json
import os

from morpho.utilities import morphologging
logger=morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)

class IO_Processor:
    '''
    IO_Processor
    All Processors will be implemented in a child class where the 
    specifics are encoded by overwriting Configure and Run.
    '''

    def __init__(self, name, *args, **kwargs):
        self.__name = name
        return


    def Configure(self, params):

        '''
        This method will be called by nymph to configure the processor
        '''

        supported_processors = {'R': IO_R_Processor, \
                                'cvs': IO_CVS_Processor, \
                                'root': IO_ROOT_Processor, \
                                'cicada': IO_CICADA_Processor}

        self.params = params
        self.file_name = read_param(params, 'filename', None)
        self.file_type = read_param(params, "format", None)
        self.file_action = read_param(params, "action", "read")

        self.processor = supported_processors[self.file_type]

        if (self.processor == None):
            logger.error("This file type is not supported or unspecified.")
            raise

    def Run(self):
        '''
        This method will be called by nymph to run the processor
        '''

        theData = self.processor(file_name, file_action)

        add_dict_param(self.params, 'data', theData)

        return self.params
