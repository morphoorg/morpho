'''
Base input/output processor for reading and writing operations
'''

from __future__ import absolute_import

from morpho.processors import BaseProcessor
from morpho.utilities import morphologging
logger=morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)

class IOProcessor(BaseProcessor):
    '''
    IO_Processor
    All Processors will be implemented in a child class where the 
    specifics are encoded by overwriting Configure and Run.
    '''

    def Configure(self, params):

        '''
        This method will be called by nymph to configure the processor
        '''

        self.supported_processors = {'R': IORProcessor, \
                                'cvs': IOCVSProcessor, \
                                'root': IOROOTProcessor}

        self.params = params
        self.file_name = read_param(params, 'filename', "required")
        self.file_type = read_param(params, "format", "required")
        self.variable = read_param(params,"var", "required")
        self.file_action = read_param(params, "action", "read")

        self.processor = self.supported_processors[self.file_type]

        if (self.processor == None):
            logger.error("This file type is not supported or unspecified.")
            raise

    def Run(self):
        '''
        This method will be called by nymph to run the processor
        '''

        theData = self.processor(self.file_name, self.file_action, self.variable)

        # add_dict_param(self.params, 'data', theData)

        return theData
