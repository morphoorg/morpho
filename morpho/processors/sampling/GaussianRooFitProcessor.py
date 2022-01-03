'''
Processor for  linear fitting
Authors: M. Guigue
Date: 06/26/18
'''

try:
    from ROOT import RooRealVar, RooDataSet, RooArgSet, RooGaussian
except ImportError:
    pass

from morpho.utilities import morphologging, reader
from morpho.processors.sampling.RooFitInterfaceProcessor import RooFitInterfaceProcessor
logger = morphologging.getLogger(__name__)


class GaussianRooFitProcessor(RooFitInterfaceProcessor):
    '''
    Linear fit of data using RootFit Likelihood sampler.
    We redefine the _defineDataset method as this analysis requires datapoints in a 2D space.
    Users should feel free to change this method as they see fit.

    Parameters:
        varName (required): name(s) of the variable in the data
        nuisanceParams (required): parameters to be discarded at end of sampling
        interestParams (required): parameters to be saved in the results variable
        iter (required): total number of iterations (warmup and sampling)
        warmup: number of warmup iterations (default=iter/2)
        chain: number of chains (default=1)
        n_jobs: number of parallel cores running (default=1)
        binned: should do binned analysis (default=false)
        options: other options
        a (required): range of slopes (list)
        b (required): range of intercepts (list)
        x (required): range of x (list)
        y (required): range of y (list)
        witdh (required): range of width (list)

    Input:
        data: dictionary containing model input data

    Results:
        results: dictionary containing the result of the sampling of the parameters of interest
    '''

    def InternalConfigure(self, config_dict):
        super().InternalConfigure(config_dict)
        self.x_min, self.x_max = reader.read_param(config_dict, "paramRange", "required")["x"]
        self.mean_min, self.mean_max = reader.read_param(config_dict, "paramRange", "required")["mean"]
        self.width_min, self.width_max = reader.read_param(config_dict, "paramRange", "required")["width"]
        return True

    def _defineDataset(self, wspace):
        varX = RooRealVar("x", "x", min(self._data["x"]), max(self._data["x"]))
        data = RooDataSet(self.datasetName, self.datasetName, RooArgSet(varX))
        for x in self._data["x"]:
            varX.setVal(x)
            data.add(RooArgSet(varX))
        getattr(wspace, 'import')(data)
        return wspace

    def definePdf(self, wspace):
        '''
        Define the model which is that the residual of the linear fit should be normally distributed.
        '''
        logger.debug("Defining pdf")
        mean = RooRealVar("mean", "mean", 0, self.mean_min, self.mean_max)
        width = RooRealVar("width", "width", 1., self.width_min, self.width_max)
        x = RooRealVar("x", "x", 0, self.x_min, self.x_max)

        pdf = RooGaussian("pdf", "pdf", x, mean, width)
        # Save pdf: this will save all required variables and functions
        getattr(wspace, 'import')(pdf)

        return wspace
