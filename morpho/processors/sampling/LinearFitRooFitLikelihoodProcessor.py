from morpho.utilities import morphologging, reader
from morpho.processors.sampling import RooFitLikelihoodSampler
logger = morphologging.getLogger(__name__)

import ROOT

class LinearFitRooFitLikelihoodProcessor(RooFitLikelihoodSampler):
    '''
    Linear fit of data using RootFit Likelihood sampler.

    '''

    def Configure(self,config_dict = {}):
        super().Configure(config_dict)
        self.a_min, self.a_max = reader.read_param(config_dict,"paramRange", "required")["a"]
        self.b_min, self.b_max = reader.read_param(config_dict,"paramRange", "required")["b"]
        self.x_min, self.x_max = reader.read_param(config_dict,"paramRange", "required")["x"]
        self.y_min, self.y_max = reader.read_param(config_dict,"paramRange", "required")["y"]

    def definePdf(self,wspace):
        '''
        
        '''
        logger.debug("Defining pdf")
        # x = ROOT.RooRealVar("x","x")
        # y = ROOT.RooRealVar("y","y")
        a = ROOT.RooRealVar("a","a",self.a_min,self.a_max)
        b = ROOT.RooRealVar("b","b",self.b_min,self.b_max)
        x = ROOT.RooRealVar("x","x",self.x_min,self.x_max)
        y = ROOT.RooRealVar("y","y",self.y_min,self.y_max)
        width = ROOT.RooRealVar("width","width",0,1000)
        # b = ROOT.RooRealVar("b","b")
        residual = ROOT.RooFormulaVar("res","y-a*x-b", ROOT.RooArgList(x,y,a,b))
        null = ROOT.RooRealVar("null","null",0.)
        pdf = ROOT.RooGaussian("pdf","pdf",residual,null,width)


        # Save pdf: this will save all required variables and functions
        getattr(wspace,'import')(pdf)

        return wspace
