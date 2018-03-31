'''
Create a wrapping processor from a function given in a python script
'''

from __future__ import absolute_import

from morpho.utilities import morphologging, reader
from morpho.processors import BaseProcessor
logger=morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)

class ProcessorAssistant(BaseProcessor):
    '''
    Describe.
    '''

    def Configure(self,config_dict):
        '''
        Configure
        '''
        logger.info("Configure with {}".format(config_dict))
        self.module_name = str(reader.read_param(config_dict,'module_name',"required"))
        self.function_name = str(reader.read_param(config_dict,'function_name',"required"))
        self.config_dict = config_dict
        # try:
        #     modulename = 'morpho.preprocessing.'+self.module_name
        #     i = importlib.import_module("{}".format(modulename))
        # except Exception as err:
        try:
            import imp
            self.module = imp.load_source(self.module_name, self.module_name+'.py')
            # i = importlib.import_module("{}".format(minidict['module_name']))
        except Exception as err:
            logger.critical(err)
            return 0
        # else:
        #     logger.info("Doing preprocessing {} using {}".format(minidict['method_name'],minidict['module_name']+'.py'))
        # else:
        #     logger.info("Doing preprocessing {} using {}".format(minidict['method_name'],modulename))
        if hasattr(self.module,self.function_name):
            logger.info("Found {} using {}".format(self.function_name,self.module_name))
        else:
            logger.critical("Couldn't find {} using {}".format(self.function_name,self.module_name))
            return 0


    def Run(self):

        try:
            return getattr(self.module,self.function_name)(self.config_dict)
        except Exception as err:
            logger.critical(err)
            return 0
        
        

