'''
Base processor for sampling-type operations
'''

from __future__ import absolute_import

import csv

from morpho.utilities import morphologging
logger=morphologging.getLogger(__name__)

from morpho.processors.IO import IOProcessor

__all__ = []
__all__.append(__name__)

class IOCVSProcessor:
    '''
    Base IO CVS Processor
    The CVS Reader and Writer
    '''

    def IO_CVS_Processor(self, file_name, action, variables):
        '''
        This method will read or write an R file
        '''
        if (action == 'write'):
            Writer(file_name,variables)
        else:
            Reader(file_name,variables)
        

    def Reader(self, file_name,variables):
        subData = {}
        with open(file_name, 'rb') as cvs_file:
            theData = csv.DictReader(csv_file)
        for var in variables:
            if var in subData.keys():
                subData.update({str(var):theData[var]})
            else:
                logger.error("Variable {} does not exist in {}".format(var,file_name))
        return theData


    def Writer(self, file_name,variables):

        theData = self.data
        subData = {}
        for var in variables:
            if var in subData.keys():
                subData.update({str(var):theData[var]})
            else:
                logger.error("Variable {} does not exist in input data".format(var))
        with open(file_name, 'wb') as csv_file:            
            csv.DictWriter(csv_file, subData)
        return None

