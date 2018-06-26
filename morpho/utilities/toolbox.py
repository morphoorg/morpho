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
                    "connectedToAsSignal": [], #-> which processor needs the output of this processors as input
                    "connectedToAsSlot": [], #-> which processor need to give its output to this processor
                    "orderSignals": [], #-> which order for each signal
                    "isFirst": True,
                    "addedToChain": False
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

    # def _RunProcessor(self,procName):
        # a_processor = self.processors_dict['procName']
        # a_processor.Run()
        
    def _GetChainOfProcessors(self):
        for a_processor_name in self.processors_dict.keys():

            for a_connection in self.config_dict['processors-toolbox']['connections']:
                proc_signal_to_be_connected = ""
                proc_slot_to_be_connected = ""
                order = -1
                if "order" in a_connection:
                    order = a_connection["order"]
                if a_connection['slot'].split(":")[0] == a_processor_name:
                    proc_signal_to_be_connected = a_connection['signal'].split(":")[0]
                    # if order == -1:
                        # self.chainProcessors[a_processor_name]["orderSignals"].append(self.chainProcessors[a_processor_name]["orderSignals"][-1]+1)
                    # else:
                    self.processors_dict[a_processor_name]["orderSignals"].append(order)
                    self.processors_dict[a_processor_name]["connectedToAsSlot"].append(proc_signal_to_be_connected)
                if a_connection['signal'].split(":")[0] == a_processor_name:
                    proc_slot_to_be_connected = a_connection['slot'].split(":")[0]
                    self.processors_dict[a_processor_name]["connectedToAsSignal"].append(proc_slot_to_be_connected)
                # if proc_slot_to_be_connected !="" or proc_signal_to_be_connected != "":
                    # print("{} -> {} -> {}".format(proc_signal_to_be_connected,a_processor_name,proc_slot_to_be_connected))

    def _PrintChainProcessor(self):
        chainProcessorsList = []

        numberOfListedProcessors = 0
        for a_processor_name, connections in self.processors_dict.items():
            if connections["isFirst"]:
                chainProcessorsList.append(a_processor_name)
                self.processors_dict[a_processor_name]['addedToChain'] = True
                break
        numberOfListedProcessors+=1

        # while numberOfListedProcessors != len(self.chainProcessors.keys()):
        #     for a_processor_name, connections in self.chainProcessors.items():
        
                
                    
    def Run(self):
        logger.debug("Configuration:\n{}".format(json.dumps(self.config_dict, indent=4)))
        if not self._CreateAndConfigureProcessors():
            logger.error("Error while creating and configuring processors")
            return False
        self._GetChainOfProcessors()
        self._PrintChainProcessor()
        print(self.processors_dict)
        # for a_connection in self.config_dict["processors-toolbox"]['connections']:
        #     self._RunProcessor()
