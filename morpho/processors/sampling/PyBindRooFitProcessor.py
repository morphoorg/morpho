import scipy.special as scs
import numpy as np
from morpho.processors.BaseProcessor import BaseProcessor
from morpho.processors.sampling.RooFitInterfaceProcessor import RooFitInterfaceProcessor
from morpho.utilities import morphologging, reader
'''
Processor for  linear fitting
Authors: M. Guigue
Date: 06/26/18
'''

try:
    import ROOT
except ImportError:
    pass
value = ROOT.gSystem.Load("libRooFit")
if value < 0:
    print("Failed loading", value)
    exit()

logger = morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)


c = 299792458
m_kg = 9.10938291*1e-31
me_keV = 510.998
q_C = 1.60217657*1e-19
Z0 = 119.917 * np.pi
Rc = 0.06e-2
a = 1.006e-2/2
B0 = 1


def sinc(x):
    if x == 0:
        return 1
    return np.sin(x)/x


def cot(x):
    return np.cos(x)/np.sin(x)


def beta_function(n, L0, E, H, theta):

    fc11 = 1.841 * c / (2 * np.pi * a)
    gamma = 1 + E / me_keV
    wc = q_C * H / (gamma * m_kg)
    v0 = c * (1 - 1 / gamma ** 2)**0.5
    vz0 = v0 * np.cos(theta)
    wa = v0 / L0 * np.sin(theta)
    f = wc / (2 * np.pi)
    Dw = 0.5 * wc * cot(theta)**2
    vp = c/(1-(2*np.pi*fc11/(wc+Dw))**2)**0.5
    k = (wc + Dw) / vp
    zmax = L0 * cot(theta)

    return scs.jv(n, k * zmax)


class start_freq_func(ROOT.TPyMultiGenFunction):
    def __init__(self):
        print("f CREATED")
        ROOT.TPyMultiGenFunction.__init__(self, self)

    def NDim(self):
        print('PYTHON NDim Freq. called')
        return 2

    def DoEval(self, args):
        #(E, theta)
        E = args[0]
        theta = args[1]
        gamma = 1 + E / me_keV
        wc = q_C * B0 / (gamma * m_kg)
        #Dw = 0.5 * wc * cot(theta)**2
        return (wc) / (2e6 * np.pi)


class power_function(ROOT.TPyMultiGenFunction):
    def __init__(self):
        print("p CREATED")
        ROOT.TPyMultiGenFunction.__init__(self, self)

    def NDim(self):
        print('PYTHON NDim power called')
        return 3

    def DoEval(self, args):
        #(E, theta, L0)
        E = args[0]
        theta = args[1]
        L0 = args[2]
        return beta_function(n=0, L0=L0, E=E, H=B0, theta=theta)


c1 = ROOT.TCanvas("c", "c", 800, 600)
L0 = ROOT.RooRealVar('L0', 'L0', 0.3, 0, 1)

E = ROOT.RooRealVar('E', 'E', 17, 18)
theta = ROOT.RooRealVar('theta', 'theta', 89*np.pi/180, np.pi/2)


startfreq_obj = start_freq_func()
ff01 = ROOT.TPyMultiGenFunction(startfreq_obj)
# ff0 = ROOT.RooFit.bindFunction("ff0",ff01, ROOT.RooArgList(E, theta))

power_obj = power_function()
fp1 = ROOT.TPyMultiGenFunction(power_obj)
# fp = ROOT.RooFit.bindFunction("fp",fp1, ROOT.RooArgList(E, theta, L0))


class PyFunctionObject(ROOT.TPyMultiGenFunction):
    def __init__(self, pythonFunction, dimension=2):
        logger.info("Created PyFunctionObject")
        ROOT.TPyMultiGenFunction.__init__(self, self)
        self.pythonFunction = pythonFunction
        self.dimension = dimension

    def NDim(self):
        return self.dimension

    # def __call__(self, args):
    #     E = args[0]
    #     theta = args[1]
    #     L0 = args[2]
    #     return self.pythonFunction(E, theta, L0)

    def DoEval(self, args):
        # print(args)
        # x = args[0]
        # y = args[1];
        # tmp1 = y-x*x;
        # # tmp2 = 1-x;
        # return self.pythonFunction(args)
        # E = args[0]
        # theta = args[1]
        # L0 = args[2]
        test_argv = list()
        for i in range(self.dimension):
            value = args[i]
            test_argv.append(value)
        # print("argv",*argv)
        # print("normal",E,theta,L0)
        return self.pythonFunction(*test_argv)
        # return self.pythonFunction(E, theta, L0)


class PyBindRooFitProcessor(RooFitInterfaceProcessor):
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
        self.ranges = reader.read_param(config_dict, "paramRange", "required")
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

    def _defineDataset(self, wspace):
        rooVarSet = set()

        for aVarName in self.ranges.keys():
            rooVarSet.add(ROOT.RooRealVar(str(aVarName), str(aVarName), min(
                self._data[aVarName]), max(self._data[aVarName])))
        # data = ROOT.RooDataSet(self.datasetName, self.datasetName, ROOT.RooArgSet(*rooVarSet))
        # for x in self._data["x"]:
        #     varX.setVal(x)
        #     data.add(ROOT.RooArgSet(varX))
        # getattr(wspace, 'import')(data)
        return wspace

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
            if aVarName in self.fixedParameters.keys():
                logger.debug("{} is fixed".format(aVarName))
                rooVarSet.append(ROOT.RooRealVar(str(aVarName), str(aVarName), self.fixedParameters[aVarName]))
            else:
                aVarSampling = ROOT.RooRealVar(str(aVarName), str(aVarName), self.ranges[aVarName][0], self.ranges[aVarName][1])
                rooVarSet.append(aVarSampling)

        self.func = getattr(self.module, self.function_name)
        self.f = PyFunctionObject(self.func, len(rooVarSet))
        self.bindFunc = ROOT.RooFit.bindFunction("test", self.f, ROOT.RooArgList(*rooVarSet))


        a0 = ROOT.RooRealVar("a0","a0",0); 
        a0.setConstant(); 
        # RooChebychev will make a first order polynomial, set to a constant 
        bkg = ROOT.RooChebychev("a0_bkg","a0_bkg",aVarSampling, ROOT.RooArgList(a0))
        # RooAbsReal *LSfcn = bindFunction(SH,m, RooArgList(deltaM,cw));//deltaM and cw are parameters 
        self.pdf = ROOT.RooRealSumPdf("pdf","pdf",self.bindFunc,bkg,ROOT.RooFit.RooConst(1.)) #; //combine the constant term (bkg)

        print("pdf:", self.pdf)
        getattr(wspace, 'import')(self.pdf)

        return wspace


if __name__ == "__main__":
    rose = RosenBrock()
    f = ROOT.TPyMultiGenFunction(rose)
    x = ROOT.RooRealVar("x", "x", 0, 10)
    a = ROOT.RooRealVar("a", "a", 1, 2)
    fx = ROOT.RooFit.bindFunction("test", f, ROOT.RooArgList(x, a))
