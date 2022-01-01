'''
R IO processor
Authors: M. Guigue
Date: 06/26/18
'''

from __future__ import absolute_import

import os

from morpho.utilities import morphologging
logger = morphologging.getLogger(__name__)

from morpho.processors.IO import IOProcessor

__all__ = [__name__]


class IORProcessor(IOProcessor):
    '''
    Base IO R Processor
    The R Reader and Writer use pystan.misc package

    Parameters:
        filename (required): path/name of file
        variables (required): variables to extract
        action: read or write (default="read")

    Input:
        None

    Results:
        data: dictionary containing the data
    '''

    def Reader(self):
        logger.debug("Reading {}".format(self.file_name))
        if os.path.exists(self.file_name):
            try:
                theData = pystan.misc.read_rdump(self.file_name)
                # theData = dict(reader)
            except:
                logger.error("Error while reading {}".format(self.file_name))
                raise
        else:
            logger.error("File {} does not exist".format(self.file_name))
            raise FileNotFoundError(self.file_name)

        logger.debug("Extracting {} from data".format(self.variables))
        for var in self.variables:
            if var in theData.keys():
                self.data.update({str(var): theData[var]})
            else:
                logger.error("Variable {} does not exist in {}".format(
                    self.variables, self.file_name))
        return True

    def Writer(self):

        logger.debug("Extracting {} from data".format(self.variables))
        subData = {}
        for var in self.variables:
            subData.update({var: self.data[var]})

        logger.debug("Saving data in {}".format(self.file_name))
        try:
            rdir = os.path.dirname(self.file_name)
            if rdir != '' and not os.path.exists(rdir):
                os.makedirs(rdir)
                logger.info("Creating folder: {}".format(rdir))
            pystan.misc.stan_rdump(subData, self.file_name)
        except:
            logger.error("Error while writing {}".format(self.file_name))
            raise
        logger.debug("File saved!")
        return True
