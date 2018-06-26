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
        self.processors_dict = dict()
        self._chain_processors = []
        self.processors_names = []

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
                logger.error("Could not create processor <{}>; exiting".format(a_dict["name"]))
                return False
        for name,processor in self.processors_dict.items():
            procName = processor["object"].name
            if procName in self.config_dict.keys():
                config_dict = self.config_dict[procName]
            else:
                config_dict = dict()
            try:
                processor["object"].Configure(config_dict)
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
            logger.error("Cannot import module {}".format(module_name))
            return False

        try:
            self.processors_dict.update({procName: 
                {
                    "object": getattr(module,processor_name)(procName),
                    "variableToGive": [],    #-> variable to give after execution
                    "procToBeConnectedTo": [], #-> which processor need to give its output to this processor
                    "varToBeConnectedTo": [], #-> which variable of the connected processor to be set
                    "isFirst": True,
                    "addedToChain": False,
                    "order_in_chain": True
                }
            })
            logger.info("Processor <{}> ({}:{}) created".format(procName,module_name,processor_name))
            return True
        except:
            logger.error("Cannot import {} from {}".format(processor_name,"morpho"))
            return False

    def _ConnectProcessors(self,signal,slot):
        if ":" not in slot:
            logger.error("Wrong signal format ({})".format(slot))
            return False
        out_processor, out_variable = slot.split(":")
        if ":" not in signal:
            logger.error("Wrong signal format ({})".format(signal))
            return False
        in_processor, in_variable = signal.split(":")

    def _DefineChain(self):
        order_in_chain = 0
        for a_connection in self.config_dict['processors-toolbox']['connections']:
            if a_connection['slot'].split(":")[0] not in self.processors_dict.keys():
                logger.error("Processor <> not defined but used as signal emitter".format(a_connection['slot'].split(":")[0]))
            if a_connection['signal'].split(":")[0] not in self.processors_dict.keys():
                logger.error("Processor <> not defined but used as connection".format(a_connection['signal'].split(":")[0]))
                
            proc_name = a_connection['signal'].split(":")[0]
            new_proc_name = a_connection['slot'].split(":")[0]

            self.processors_dict[proc_name]["variableToGive"].append(a_connection['signal'].split(":")[1])
            self.processors_dict[proc_name]["procToBeConnectedTo"].append(a_connection['slot'].split(":")[0])
            if proc_name not in self._chain_processors:
                self._chain_processors.append(proc_name)
            if new_proc_name not in self._chain_processors:
                self._chain_processors.append(new_proc_name)
            self.processors_dict[proc_name]["varToBeConnectedTo"].append(a_connection['slot'].split(":")[1])
            # self.processors_dict[proc_name]['order_in_chain'].append(order_in_chain)
            order_in_chain += 1
        for a_processor in self.processors_dict.keys():
            if a_processor not in self._chain_processors:
                self._chain_processors.append(a_processor)
        logger.debug("Sequence of processors: {}".format(self._chain_processors))

    def _RunChain(self):
        for a_processor in self._chain_processors:
            try:
                self.processors_dict[a_processor]['object'].Run()
            except:
                logger.error("Error")

    def Run(self):
        logger.debug("Configuration:\n{}".format(json.dumps(self.config_dict, indent=4)))
        if not self._CreateAndConfigureProcessors():
            logger.error("Error while creating and configuring processors")
            return False
        self._DefineChain()
        self._RunChain()
