'''
Base input/output processor for reading and writing operations
'''

from __future__ import absolute_import

from morpho.processors import BaseProcessor
from morpho.utilities import morphologging, reader
logger=morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)

class IOProcessor(BaseProcessor):
    '''
    IO_Processor
    All Processors will be implemented in a child class where the
    specifics are encoded by overwriting Configure and Run.
    '''

    def Reader(self):
        '''
        Need to be defined by the child class
        '''
        logger.error("Default Reader method: need to implement your own")
        raise

    def Writer(self):
        '''
        Need to be defined by the child class
        '''
        logger.error("Default Writer method: need to implement your own")
        raise

    def InternalConfigure(self, params):

        '''
        This method will be called by nymph to configure the processor
        '''
        self.params = params
        self.file_name = reader.read_param(params, 'filename', "required")
        self.variables = reader.read_param(params,"variables", "required")
        self.file_action = reader.read_param(params, "action", "read")
        self.data = dict()
        return True

    def InternalRun(self):
        '''
        This method will read or write an file
        '''
        if (self.file_action == 'write'):
            return self.Writer()
        else:
            return self.Reader()
        return False
