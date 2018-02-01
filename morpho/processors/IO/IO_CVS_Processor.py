'''
Base processor for sampling-type operations
'''

from __future__ import absolute_import

import json
import os
import CSV

from morpho.utilities import morphologging
logger=morphologging.getLogger(__name__)

from morpho.processors.io_processors import IO_Processors

__all__ = []
__all__.append(__name__)

class IO_CVS_Processor:
    '''
    Base IO CVS Processor
    The CVS Reader and Writer
    '''

    def __init__(self, name, *args, **kwargs):
        self.__name = name
        return

    def IO_CVS_Processor(self, file_name, action='read'):
        '''
        This method will read or write an R file
        '''
        if (action == 'write'):
            Writer(file_name)
        else:
            Reader(file_name)
        

    def Reader(self, file_name):
        with open(file_name, 'rb') as cvs_file:
            theData = csv.DictReader(csv_file)
        return theData


    def Writer(self, file_name):

        theData = self.data
        with open(file_name, 'wb') as csv_file:            
            csv.DictWriter(csv_file, theData)
        return None

