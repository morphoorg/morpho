#!/bin/python

from morpho.utilities import morphologging
logger=morphologging.getLogger(__name__)

import json, yaml
import os, importlib

class ToolBox:
    def __init__(self, filename=""):
        logger.info("ToolBox!")
        self._ReadConfigFile(filename)
        self.processors_definition = self.config_dict
        self.processors_list = []
        self.processors_names = []
        # self.connections_definition = self.config_dict.get("processors-toolbox")

    def _ReadConfigFile(self, filename):
        if os.path.exists(filename):
            if filename.endswith(".json"):
                self.my_module = importlib.import_module("json")
            elif filename.endswith(".yaml"):
                self.my_module = importlib.import_module("yaml")
            else:
                logger.error("Unknown format: {}".format(filename))
                raise 
            with open(filename, 'r') as json_file:
                try:
                    self.config_dict = self.my_module.load(json_file)
                except:
                    logger.error("Error while reading {}".format(filename))
                    raise
        else:
            logger.error("File {} does not exist".format(filename))
            raise FileNotFoundError(filename)
    
    def _CreateAndConfigureProcessors(self):
        for a_dict in self.config_dict["processors-toolbox"]["processors"]:
            if not self._CreateOneProcessor(a_dict["name"],a_dict["type"]):
                logger.error("Could not create processor; exiting")
                return False
        for processor in self.processors_list:
            procName = processor.name
            if procName in self.config_dict.keys():
                config_dict = self.config_dict[procName]
            else:
                config_dict = dict()
            try:
                processor.Configure(config_dict)
            except:
                logger.error("Configuration of <{}> failed".format(procName))
                return False
        return True

    def _CreateOneProcessor(self,procName,procClass):
        # Parsing procClass
        if ":" in procClass:
            (module_name, processor_name) = procClass.split(":")
        else:
            module_name = "morpho"
            processor_name = procClass
        # importing module (morpho is default)
        try:
            module = importlib.import_module(module_name)
        except:
            logger.error("Cannot import module {} for processor {}".format(module_name,processor_name))
            return False

        logger.debug("trying to import processor {} from {}".format(processor_name,module_name))
        try:
            self.processors_list.append(getattr(module,processor_name)(procName))
            return True
        except:
            logger.error("Cannot import {} from {}".format(processor_name,"morpho"))
            return False

    def _ConnectProcessors(self,signal,slot):
        if ":" in procName:
            print(split(procName),":")

    # def _RunProcessors(self):
        
