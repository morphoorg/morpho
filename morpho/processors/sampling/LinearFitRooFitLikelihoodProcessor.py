from morpho.utilities import morphologging, reader
from morpho.processors.sampling import RooFitLikelihoodSampler
# from RooFitLikelihoodSampler import RooFitLikelihoodSampler
logger = morphologging.getLogger(__name__)

import Constants

import ROOT

class LinearFitRooFitLikelihoodSampler(RooFitLikelihoodSampler):

    def definePdf(self,wspace):
        '''
        Defines the Pdf that RooFit will sample and add it to the workspace.
        The Workspace is then returned by the user.
        Users should edit this function.
        '''
        logger.debug("Defining pdf")
        var = wspace.var(self.varName)

        return wspace
