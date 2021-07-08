from morpho.processors.BaseProcessor import BaseProcessor
from morpho.processors.sampling.RooFitInterfaceProcessor import RooFitInterfaceProcessor
from morpho.utilities import morphologging, reader
'''
Processor for  linear fitting
Authors: M. Guigue
Date: 06/26/18
'''

import ROOT

value = ROOT.gSystem.Load("libRooFit")
if value < 0:
    print("Failed loading", value)
    exit()

logger = morphologging.getLogger(__name__)

# Dynamic inheritance of PyFunctionObject
# Prior to ROOT v6.22, TPyMultiGenFunction was used to wrap ROOT::Math::IMultiGenFunction.
# As of ROOT v6.22, TPyMultiGenFunction no longer exists, and cppyy is used to automatically create a wrapper around IMultiGenFunction.
try:
    from ROOT import TPyMultiGenFunction
except:
    parent = ROOT.Math.IMultiGenFunction
    using_tpy = False
else:
    parent = ROOT.TPyMultiGenFunction
    using_tpy = True

class PyFunctionObject(parent):
    def __init__(self, pythonFunction, dimension=2):
        logger.info("Created PyFunctionObject")
        if using_tpy:
            super().__init__(self)
        self.pythonFunction = pythonFunction
        self.dimension = dimension

    def NDim(self):
        return self.dimension

    def DoEval(self, args):
        test_argv = list()
        for i in range(self.dimension):
            value = args[i]
            test_argv.append(value)
        return self.pythonFunction(*test_argv)


class PyBindRooFitProcessor(RooFitInterfaceProcessor):
    '''
    Linear fit of data using RootFit Likelihood sampler.
    We redefine the _defineDataset method as this analysis requires datapoints in a 2D space.
    Users should feel free to change this method as they see fit.

    Parameters:
        varName (required): name(s) of the variable in the data
        nuisanceParams (required): parameters to be discarded at end of sampling
        interestParams (required): parameters to be saved in the results variable
        paramRange (required): range of parameters (defined as <{'a': [a_min, a_max]}>)
        initValues: initial value (defined as <{'a': a_init}>)
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
        self.ranges = reader.read_param(config_dict, "paramRange", "required")
        self.initParamValues = reader.read_param(
            config_dict, "initValues", dict())
        self.module_name = reader.read_param(
            config_dict, "module_name", "required")
        self.function_name = reader.read_param(
            config_dict, "function_name", "required")
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
        # for varName in self.varName:
        #     if varName not in self.ranges.keys():
        #         logger.error("Missing range for {}".format(varName))
        #         return False
        # self.x_min, self.x_max = reader.read_param(config_dict, "paramRange", "required")["x"]
        # self.mean_min, self.mean_max = reader.read_param(config_dict, "paramRange", "required")["mean"]
        # self.width_min, self.width_max = reader.read_param(config_dict, "paramRange", "required")["width"]

        # return True

    # def _defineDataset(self, wspace):
    #     rooVarSet = set()

    #     for aVarName in self.ranges.keys():
    #         rooVarSet.add(ROOT.RooRealVar(str(aVarName), str(aVarName), min(
    #             self._data[aVarName]), max(self._data[aVarName])))
        # data = ROOT.RooDataSet(self.datasetName, self.datasetName, ROOT.RooArgSet(*rooVarSet))
        # for x in self._data["x"]:
        #     varX.setVal(x)
        #     data.add(ROOT.RooArgSet(varX))
        # getattr(wspace, 'import')(data)
        # return wspace

    def definePdf(self, wspace):
        '''
        Define the model which is that the residual of the linear fit should be normally distributed.
        '''
        logger.debug("Defining pdf")
        # mean = ROOT.RooRealVar("mean", "mean", 0, self.mean_min, self.mean_max)
        # width = ROOT.RooRealVar("width", "width", 1., self.width_min, self.width_max)
        # x = ROOT.RooRealVar("x", "x", 0, self.x_min, self.x_max)

        rooVarSet = list()
        aVarSampling = 0
        for aVarName in self.ranges.keys():
            logger.info(aVarName)
            if aVarName in self.fixedParameters.keys():
                logger.debug("{} is fixed".format(aVarName))
                rooVarSet.append(ROOT.RooRealVar(str(aVarName), str(
                    aVarName), self.fixedParameters[aVarName]))
                logger.info(aVarName)
            elif aVarName in self.initParamValues.keys():
                aVarSampling = ROOT.RooRealVar(str(aVarName), str(
                    aVarName), self.initParamValues[aVarName], self.ranges[aVarName][0], self.ranges[aVarName][1])
                rooVarSet.append(aVarSampling)
                logger.info(aVarName)
            else:
                aVarSampling = ROOT.RooRealVar(str(aVarName), str(
                    aVarName), self.ranges[aVarName][0], self.ranges[aVarName][1])
                rooVarSet.append(aVarSampling)
                logger.info(aVarName)

        self.func = getattr(self.module, self.function_name)
        self.f = PyFunctionObject(self.func, len(rooVarSet))
        self.bindFunc = ROOT.RooFit.bindFunction(
            "test", self.f, ROOT.RooArgList(*rooVarSet))

        a0 = ROOT.RooRealVar("a0", "a0", 0)
        a0.setConstant()
        # RooChebychev will make a first order polynomial, set to a constant
        bkg = ROOT.RooChebychev(
            "a0_bkg", "a0_bkg", aVarSampling, ROOT.RooArgList(a0))
        # RooAbsReal *LSfcn = bindFunction(SH,m, RooArgList(deltaM,cw));//deltaM and cw are parameters
        self.pdf = ROOT.RooRealSumPdf("pdf", "pdf", self.bindFunc, bkg, ROOT.RooFit.RooConst(
            1.))  # ; //combine the constant term (bkg)

        logger.debug("pdf: {}".format(self.pdf))
        wspace.Print()
        getattr(wspace, 'import')(self.pdf)

        return wspace


if __name__ == "__main__":
    rose = RosenBrock()
    if using_tpy:
        f = ROOT.TPyMultiGenFunction(rose)
    else:
        f = ROOT.Math.IMultiGenFunction(rose)
    x = ROOT.RooRealVar("x", "x", 0, 10)
    a = ROOT.RooRealVar("a", "a", 1, 2)
    fx = ROOT.RooFit.bindFunction("test", f, ROOT.RooArgList(x, a))
