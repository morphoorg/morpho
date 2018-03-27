'''
'''

from __future__ import absolute_import


# import json as mymodule
import importlib
import os

from morpho.utilities import morphologging
logger=morphologging.getLogger(__name__)

from morpho.processors.IO import IOProcessor

__all__ = []
__all__.append(__name__)

class IOJSONProcessor(IOProcessor):
    '''
    Base IO JSON Processor
    '''

    module_name = 'json'
    dump_kwargs = {"indent": 4}

    def __init__(self,name):
        super().__init__(name)
        self.my_module = importlib.import_module(self.module_name)

    def Reader(self):
        logger.debug("Reading {}".format(self.file_name))
        subData = {}
        if os.path.exists(self.file_name):
            with open(self.file_name, 'r') as json_file:
                try:
                    theData = self.my_module.load(json_file)
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


    def Writer(self):
        logger.debug("Saving data in {}".format(self.file_name))
        rdir = os.path.dirname(self.file_name)
        if rdir != '' and not os.path.exists(rdir):
            os.makedirs(rdir)
            logger.debug("Creating folder: {}".format(rdir))
        logger.debug("Extracting {}".format(self.variables))
        subData = {}
        for item in self.variables:
            if item['variable'] in self.data.keys():
                alias = item.get("json_alias") or item['variable']
                subData.update({str(alias):self.data[item['variable']]})
            else:
                logger.error("Variable {} does not exist in {}".format(self.variables,self.file_name))
        with open(self.file_name, 'w') as json_file:
            try:
                self.my_module.dump(subData, json_file, **self.dump_kwargs)
            except:
                logger.error("Error while writing {}".format(self.file_name))
                raise
        logger.debug("File saved!")
        return None

class IOYAMLProcessor(IOJSONProcessor):
    '''
    IO YAML Processor: uses IOJSONProcessor as basis
    '''

    module_name = 'yaml'
    
    