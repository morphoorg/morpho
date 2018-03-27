'''
'''

from __future__ import absolute_import

import csv
import os
import numpy as np

from morpho.utilities import morphologging, reader
logger=morphologging.getLogger(__name__)

from morpho.processors.IO import IOProcessor

__all__ = []
__all__.append(__name__)

class IOROOTProcessor(IOProcessor):
    '''
    Base IO ROOT Processor
    The ROOT Reader and Writer
    '''

    def Configure(self, params):
        super().Configure(params)
        self.tree_name = reader.read_param(params,"tree_name","required")
        self.file_option = reader.read_param(params,"file_option","Recreate")

    def Reader(self):
        logger.debug("Reading {}".format(self.file_name))
        
        import uproot
        subData = {}
        for key in self.variables:
            subData.update({str(key): []})
        tree = uproot.open(self.file_name)[self.tree_name]
        for data in tree.iterate(self.variables):
            for key, value in data.items():
                varName = key.decode("utf-8") 
                subData.update({str(varName): subData[str(varName)] + value.tolist()})
        return subData


    def _branch_element_type(self,element):
        if isinstance(element,int):
            return "I"
        elif isinstance(element,float):
            return "F"
        else:
            logger.warning("{} not supported; using float".format(type(element)))
            return "F"
    def _get_zero_with_type(self,a_type):
        if a_type=="F":
            return 0.
        elif a_type=="I":
            return 0
        else:
            logger.warning("{} not supported; using float".format(a_type))
            return 0.

    def Writer(self):

        logger.debug("Saving data in {}".format(self.file_name))

        rdir = os.path.dirname(self.file_name)
        if not rdir=="" and not os.path.exists(rdir):
            os.makedirs(rdir)
            logger.debug("Creating folder: {}".format(rdir))
        
        import numpy as np
        logger.debug("Writing a tree")
        import ROOT

        f = ROOT.TFile(self.file_name, self.file_option)
        t = ROOT.TTree(self.tree_name, self.tree_name)
        info_data = {}
        numberData = -1
        hasUpdatedNumberData = False
        # Determine general properties of the tree: type and size of branches, number of iterations for the tree
        for key in self.variables:
            if numberData<len(self.data[key]):
                if hasUpdatedNumberData:
                    logger.warning("Number of datapoints updated more than once: potential problem with input data")
                logger.debug("Updating number datapoints")
                numberData = len(self.data[key])
                hasUpdatedNumberData = True
            if isinstance(self.data[key][0],list):
                info_subDict = {
                    "len": len(self.data[key][0]),
                    "type": self._branch_element_type(self.data[key][0][0])
                }
            else:
                info_subDict = {
                    "len": 0,
                    "type": self._branch_element_type(self.data[key][0])
                }
            info_data.update({str(key):info_subDict})   

        # Create an empty class where the attributes will be used to write the tree
        class AClass(object): pass
        tempObject=AClass()

        logger.debug("Creating branches")
        from array import array
        for key in info_data:
            if info_data[key]["len"]==0:
                setattr(tempObject, str(key), array( info_data[key]['type'].lower(), [ self._get_zero_with_type(info_data[key]['type']) ]))
                t.Branch( str(key), getattr(tempObject,str(key)), '{}/{}'.format(str(key),info_data[key]['type']) )
            else:
                setattr(tempObject, str(key), array( info_data[key]['type'].lower(), int(info_data[key]['len']) * [ self._get_zero_with_type(info_data[key]['type']) ]))     
                t.Branch( str(key), getattr(tempObject,str(key)), '{}[{}]/{}'.format(str(key),info_data[key]['len'],info_data[key]['type']) )                           

        logger.debug("Adding data")
        for i in range(numberData):
            for key in info_data:
                temp_var = getattr(tempObject,str(key))
                if info_data[key]["len"]==0:
                    temp_var[0] = self.data[str(key)][i]
                else:
                    for j in range(info_data[key]["len"]):
                        temp_var[j] = self.data[str(key)][i][j]
                setattr(tempObject,str(key) ,temp_var)
            t.Fill()
        f.cd()
        t.Write()
        f.Close()
        logger.debug("File saved!")
        return None

