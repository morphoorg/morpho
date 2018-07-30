#!/bin/python

'''
Toolbox class: create, configure and run processors
Authors: M. Guigue
Date: 06/26/18
'''
import os
import importlib

from morpho.utilities import morphologging, parser
logger = morphologging.getLogger(__name__)


class ToolBox:
    '''
    Manages processors requested by the user at run-time.
    Via a configuration file, the user defines which processor to use, how to
    configure them and how to connect them.
    '''

    def __init__(self, args):
        self._ReadConfigFile(args.config)
        self._UpdateConfigFromCLI(args)
        self._processors_dict = dict()
        self._chain_processors = []

    def _ReadConfigFile(self, filename):
        if os.path.exists(filename):
            if filename.endswith(".json"):
                my_module = importlib.import_module("json")
            elif filename.endswith(".yaml"):
                my_module = importlib.import_module("yaml")
            else:
                logger.warning(
                    "Unknown format: {}; trying json".format(filename))
                my_module = importlib.import_module("json")
            with open(filename, 'r') as json_file:
                try:
                    self.config_dict = my_module.load(json_file)
                except Exception as err:
                    logger.error(
                        "Error while reading {}:\n{}".format(filename, err))
                    raise
        else:
            logger.error("File {} does not exist".format(filename))
            raise FileNotFoundError(filename)

    def _UpdateConfigFromCLI(self, args):
        if "param" in args and args.param:
            self.config_dict = parser.update_from_arguments(
                self.config_dict, args.param)

    def _CreateAndConfigureProcessors(self):
        for a_dict in self.config_dict["processors-toolbox"]["processors"]:
            if not self._CreateOneProcessor(a_dict["name"], a_dict["type"]):
                logger.error(
                    "Could not create processor <{}>; exiting".format(a_dict["name"]))
                return False
        for _, processor in self._processors_dict.items():
            procName = processor["object"].name
            if procName in self.config_dict.keys():
                config_dict = self.config_dict[procName]
            else:
                config_dict = dict()
            try:
                processor["object"].Configure(config_dict)
            except Exception as err:
                logger.error(
                    "Configuration of <{}> failed: \n{}".format(procName, err))
                return False
        return True

    def _CreateOneProcessor(self, procName, procClass):
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
            self._processors_dict.update({procName:
                                          {
                                              "object": getattr(module, processor_name)(procName),
                                              "variableToGive": [],  # -> variable to give after execution
                                              # -> which processor need to give its output to this processor
                                              "procToBeConnectedTo": [],
                                              "varToBeConnectedTo": [],  # -> which variable of the connected processor to be set
                                              "deleted": False
                                          }
                                          })
            logger.info("Processor <{}> ({}:{}) created".format(
                procName, module_name, processor_name))
            return True
        except:
            logger.error("Cannot import {} from {}".format(
                processor_name, "morpho"))
            return False

    def _ConnectProcessors(self, nameProc):
        proc_object = self._processors_dict[nameProc]['object']
        nConnections = len(self._processors_dict[nameProc]['variableToGive'])
        for i in range(nConnections):
            proc_name_to_update = self._processors_dict[nameProc]['procToBeConnectedTo'][i]
            var_to_give = self._processors_dict[nameProc]['variableToGive'][i]
            var_to_be_connected_to = self._processors_dict[nameProc]['varToBeConnectedTo'][i]
            proc_object_to_update = self._processors_dict[proc_name_to_update]['object']
            logger.debug("Connection {}:{} -> {}:{}".format(nameProc,
                                                            var_to_give, proc_name_to_update, var_to_be_connected_to))

            try:
                val = getattr(proc_object, var_to_give)
                setattr(proc_object_to_update, var_to_be_connected_to, val)
            except Exception as err:
                logger.error("Connection {}:{} -> {}:{} failed:\n{}".format(nameProc, var_to_give, proc_name_to_update, var_to_be_connected_to, err))
                return False
        return True

    def _DefineChain(self):
        '''
        Defines the connections between the processors and place the processors into a ordered list.
        '''
        for a_connection in self.config_dict['processors-toolbox']['connections']:
            if a_connection['slot'].split(":")[0] not in self._processors_dict.keys():
                logger.error("Processor <{}> not defined but used as signal emitter".format(
                    a_connection['slot'].split(":")[0]))
            if a_connection['signal'].split(":")[0] not in self._processors_dict.keys():
                logger.error("Processor <{}> not defined but used as connection".format(
                    a_connection['signal'].split(":")[0]))
            proc_name = a_connection['signal'].split(":")[0]
            new_proc_name = a_connection['slot'].split(":")[0]
            self._processors_dict[proc_name]["variableToGive"].append(
                a_connection['signal'].split(":")[1])
            self._processors_dict[proc_name]["procToBeConnectedTo"].append(
                a_connection['slot'].split(":")[0])
            if proc_name not in self._chain_processors:
                self._chain_processors.append(proc_name)
            if new_proc_name not in self._chain_processors:
                self._chain_processors.append(new_proc_name)
            self._processors_dict[proc_name]["varToBeConnectedTo"].append(
                a_connection['slot'].split(":")[1])
        for a_processor in self._processors_dict.keys():
            if a_processor not in self._chain_processors:
                self._chain_processors.append(a_processor)
        logger.debug("Sequence of processors: {}".format(
            self._chain_processors))
        return True

    def _RunChain(self):
        '''
        Execute the chain of processors
        '''
        for a_processor in self._chain_processors:
            try:
                if not self._processors_dict[a_processor]['object'].Run():
                    logger.error("Result <{}> incorrect".format(a_processor))
                    return False
            except Exception as err:
                logger.error(
                    "Error while running <{}>:\n{}".format(a_processor, err))
                raise err
            self._ConnectProcessors(a_processor)
            if self._processors_dict[a_processor]['object'].delete:
                self._processors_dict[a_processor]['deleted'] = True
                logger.info("Deleting <{}>".format(a_processor))
                del self._processors_dict[a_processor]['object']
        return True

    def Run(self):
        import json
        logger.debug("Configuration:\n{}".format(
            json.dumps(self.config_dict, indent=4)))
        if not self._CreateAndConfigureProcessors():
            logger.error("Error while creating and configuring processors!")
            return False
        if not self._DefineChain():
            logger.error("Error while defining processors chain!")
            return False
        if not self._RunChain():
            logger.error("Error while running processors!")
            return False

    def GetProcessor(procName):
        if self._processors_dict[str(procName)]['deleted']:
            logger.warning("Processor {} has been deleted!".format(procName))
            return 0
        return self._processors_dict[str(procName)]['object']

    def GetProcAttr(procName, varName):
        if self._processors_dict[str(procName)]['deleted']:
            logger.warning("Processor {} has been deleted!".format(procName))
            return 0
        value = 0
        try:
            value = getattr(self._processors_dict[str(procName)]['object'], str(varName))
        except:
            logger.warning("Attribute {} does not exist in {}".format(procValue, procName))
        return value
        
