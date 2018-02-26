'''
Base processor for sampling-type operations
'''

from __future__ import absolute_import

import ROOT as root

from morpho.utilities import morphologging
logger=morphologging.getLogger(__name__)

from morpho.processors.io_processors import IO_Processors

__all__ = []
__all__.append(__name__)

class IO_ROOT_Processor:
    '''
    Base IO ROOT Processor
    The R Reader and Writer
    '''

    def IO_ROOT_Processor(self, file_name, action='read'):
        '''
        This method will read or write an R file
        '''
        if (action == 'write'):
            Writer(file_name)
        else:
            Reader(file_name)
        

    def Reader(self, file_name):

        tree_name = read_param(self, 'tree_name', 'tree')

        theFile =  root.TFile(file_name)
        theData =  theFile.Get(tree_name)

        return theData


    def Writer(self, file_name):

        tree_name = read_param(self, 'tree_name', 'tree')
        theData = self.data

        theFile = root.TFile(file_name, "recreate")
        theTree = root.TTree(tree_name)

        theTree.Fill()

        theFile.Write()
        theFile.Close()

        return None

