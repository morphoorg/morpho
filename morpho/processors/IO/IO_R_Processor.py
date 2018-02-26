'''
Base processor for sampling-type operations
'''

from __future__ import absolute_import

import pystan

from morpho.utilities import morphologging
logger=morphologging.getLogger(__name__)

from morpho.processors.io_processors import IO_Processors

__all__ = []
__all__.append(__name__)

class IO_R_Processor:
    '''
    Base IO R Processor
    The R Reader and Writer
    '''

    def IO_R_Processor(self, file_name, action='read'):
        '''
        This method will read or write an R file
        '''
        if (action == 'write'):
            Writer(file_name)
        else:
            Reader(file_name)
        

    def Reader(self, file_name):

        theData = pystan.misc.read_rdump(file_name)
        return theData


    def Writer(self, file_name):

        theData = self.data
        pystan.misc.read_rdump(theData, file_name)
        return None

