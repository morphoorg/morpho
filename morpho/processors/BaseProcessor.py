"""
Base processor for sampling-type operations
Authors: J. Johnston, M. Guigue, T. Weiss
Date: 06/26/18
"""

from __future__ import absolute_import
import abc
import six

from morpho.utilities import morphologging
logger = morphologging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class BaseProcessor():
    """
    Base Processor
    All Processors will be implemented in a child class where the
    specifics are encoded by overwriting Configure and Run.

    Parameters:
        delete: do delete processor after running

    Input:
        None

    Results:
        None
    """
    def __init__(self, name):
        self._processor_name = name
        logger.debug(f"Creating processor <{self._processor_name}>")
        self._delete_processor = True

    @property
    def name(self):
        return self._processor_name

    @property
    def delete(self):
        return self._delete_processor

    def Configure(self, params) -> bool:
        '''
        This method will be called by nymph to configure the processor
        '''
        logger.info(f"Configure <{self.name}>")
        if "delete" in params:
            self._delete_processor = params['delete']
        if not self.InternalConfigure(params):
            logger.error(f'Error while configuring <{self.name}>')
            return False
        return True

    @abc.abstractmethod
    def InternalConfigure(self, params) -> bool:
        '''
        Method called by Configure() to set up the object. Must be
        overridden by child class.
        '''
        return False

    def Run(self) -> bool:
        '''
        This method will be called by nymph to run the processor
        '''
        logger.info(f"Run <{self.name}>...")
        if not self.InternalRun():
            logger.error(f"Error while running <{self.name}>")
            return False
        logger.info(f"Done with <{self.name}>")
        return True

    @abc.abstractmethod
    def InternalRun(self) -> bool:
        '''
        Method called by Run() to run the object. Must be
        overridden by child class.
        '''
        return False
