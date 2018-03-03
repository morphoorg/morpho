'''
'''

from __future__ import absolute_import

import csv
import os

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
        subData = {}
        logger.debug("Reading {}".format(self.file_name))
        if os.path.exists(self.file_name):
            with open(self.file_name, 'r') as csv_file:
                try:
                    reader = csv.reader(csv_file)
                    theData = dict(reader)
                except:
                    logger.error("Error while reading {}".format(self.file_name))
                    raise
        else:
            logger.error("File {} does not exist".format(self.file_name))
            raise FileNotFoundError(self.file_name)

        logger.debug("Extracting {}".format(self.variables))
        for var in self.variables:
            if var in theData.keys():
                subData.update({str(var):theData[var]})
            else:
                logger.error("Variable {} does not exist in {}".format(self.variables,self.file_name))
        return subData

    def _branch_element_type(self,element):
        if isinstance(element,int):
            return "I"
        elif isinstance(element,float):
            return "F"
        else:
            logger.warning("{} not supported; using float".format(type(element)))
            return "F"

    def Writer(self):

        logger.debug("Saving data in {}".format(self.file_name))

        rdir = os.path.dirname(self.file_name)
        if not rdir=="" and not os.path.exists(rdir):
            os.makedirs(rdir)
            logger.debug("Creating folder: {}".format(rdir))
        
        import numpy as np
        print("Writing a tree")
        import ROOT

        f = ROOT.TFile(self.file_name, self.file_option)
        t = ROOT.TTree(self.tree_name, self.tree_name)
        info_data = {}
        for key in self.variables:
            if not isinstance(self.data[key],list):
                print("element not a list: making a list of one element")
                self.data.update({str(key):[self.data[key]]})
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

        logger.debug("Creating branches")
        for key in info_data:
            if info_data[key]["len"]==0:
                t.Branch( str(key), n, '{}/{}'.format(key,info_data[key]['type']) )
            else:
                t.Branch( str(key), n, '{}[{}]/{}'.format(key,info_data[key]['len'],info_data[key]['type']) )
                
                     
        print(info_data)


        # with open(self.file_name, 'w') as csv_file:
        #     try:
        #         writer = csv.writer(csv_file)
        #         for key in self.variables:
        #             writer.writerow([key, self.data[key]])
        #     except:
        #         logger.error("Error while writing {}".format(self.file_name))
        #         raise
        logger.debug("File saved!")
        return None

