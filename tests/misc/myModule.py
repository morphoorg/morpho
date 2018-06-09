'''
A super simple module for unittest
'''
from morpho.utilities import morphologging
logger = morphologging.getLogger(__name__)

def myFunction(config_dict):
    logger.info("This is my function")
    logger.info("I will return: {}".format("value="+str(config_dict["value"])))
    return "value="+str(config_dict["value"])