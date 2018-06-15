#!/bin/python

from morpho.utilities import morphologging, logDictionary
logger=morphologging.getLogger(__name__)

import json, yaml
import os, importlib
import prettyprint

class ToolBox:
    def __init__(self, filename=""):
        logger.info("ToolBox!")
        self._read_config_file(filename)
        print(self.config_dict)
        self.processors_definition = self.config_dict
        # self.connections_definition = self.config_dict.get("processors-toolbox")
        logger.info(logDictionary(self.processors_definition))
        prettyprint.prettyprint(self.processors_definition)

    def _read_config_file(self, filename):
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
