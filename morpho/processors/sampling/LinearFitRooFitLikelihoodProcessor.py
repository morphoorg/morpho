from morpho.utilities import morphologging, reader
from morpho.processors.sampling import RooFitLikelihoodSampler
logger = morphologging.getLogger(__name__)

import ROOT

class LinearFitRooFitLikelihoodProcessor(RooFitLikelihoodSampler):
    '''
    Linear fit of data using RootFit Likelihood sampler.
    We redefine the _defineDataset method as this analysis requires datapoints in a 2D space.
    Users should feel free to change this method as they see fit.
    '''

    def Configure(self,config_dict = {}):
        super().Configure(config_dict)
        self.a_min, self.a_max = reader.read_param(config_dict,"paramRange", "required")["a"]
        self.b_min, self.b_max = reader.read_param(config_dict,"paramRange", "required")["b"]
        self.x_min, self.x_max = reader.read_param(config_dict,"paramRange", "required")["x"]
        self.y_min, self.y_max = reader.read_param(config_dict,"paramRange", "required")["y"]
        self.width_min, self.width_max = reader.read_param(config_dict,"paramRange", "required")["width"]

    def _defineDataset(self,wspace):
        varX = ROOT.RooRealVar("x","x",min(self._data["x"]),max(self._data["x"]))
        varY = ROOT.RooRealVar("y","y",min(self._data["y"]),max(self._data["y"]))
        data = ROOT.RooDataSet(self.datasetName,self.datasetName,ROOT.RooArgSet(varX,varY))
        for x,y in zip(self._data["x"],self._data["y"]):
            varX.setVal(x)
            varY.setVal(y)
            data.add(ROOT.RooArgSet(varX,varY))
        getattr(wspace,'import')(data)
        return wspace

    def definePdf(self,wspace):
        '''
        Define the model which is that the residual of the linear fit should be normally distributed.
        '''
        logger.debug("Defining pdf")
        a = ROOT.RooRealVar("a","a",0,self.a_min,self.a_max)
        b = ROOT.RooRealVar("b","b",0,self.b_min,self.b_max)
        width = ROOT.RooRealVar("width","width",1.,self.width_min,self.width_max)

        x = ROOT.RooRealVar("x","x",self.x_min,self.x_max)
        y = ROOT.RooRealVar("y","y",self.y_min,self.y_max)
        res = ROOT.RooFormulaVar("res","(y-a*x-b)/width", ROOT.RooArgList(x,y,a,b,width))
        null = ROOT.RooRealVar("null","null",0.)
        one = ROOT.RooRealVar("one","one",1.)

        pdf = ROOT.RooGaussian("pdf","pdf",res,null,one)
        # Save pdf: this will save all required variables and functions
        getattr(wspace,'import')(pdf)

        return wspace
