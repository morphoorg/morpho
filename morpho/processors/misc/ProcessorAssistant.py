'''
Create a wrapping processor from a function given in a python script
Authors: M. Guigue
Date: 06/26/18
'''

from __future__ import absolute_import

from morpho.utilities import morphologging, reader
from morpho.processors import BaseProcessor
logger = morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)


class ProcessorAssistant(BaseProcessor):
    '''
    Convenience wrapper that creates a processor
    around a function from an external python script
    The parameters of the function are given in the same configuration
    dictionary.

    Parameters:
        module_name (required): path/name of the python script
        function_name (required): name of the function to execute

    Input:
        None

    Results:
        results: dictionary containing the result of the function
    '''

    def InternalConfigure(self, config_dict):
        self.module_name = str(reader.read_param(config_dict, 'module_name', "required"))
        self.function_name = str(reader.read_param(config_dict, 'function_name', "required"))
        self.config_dict = config_dict
        # Test if the module exists
        try:
            import imp
            self.module = imp.load_source(
                self.module_name, self.module_name+'.py')
        except Exception as err:
            logger.critical(err)
            return 0
        # Test if the function exists in the file
        if hasattr(self.module, self.function_name):
            logger.info("Found {} using {}".format(
                self.function_name, self.module_name))
        else:
            logger.critical("Couldn't find {} using {}".format(
                self.function_name, self.module_name))
            return False
        return True

    def InternalRun(self):
        try:
            self.results = getattr(
                self.module, self.function_name)(self.config_dict)
            return True
        except Exception as err:
            logger.critical(err)
            return False
