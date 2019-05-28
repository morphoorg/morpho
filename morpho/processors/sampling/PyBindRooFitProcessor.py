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
        logger.info('PYTHON NDim called: {}'.format(self.dimension))
        return self.dimension

    def __call__(self, args):
        E = args[0]
        theta = args[1]
        L0 = args[2]
        return self.pythonFunction(E, theta, L0)

    def DoEval(self, args):
        # print(args)
        # x = args[0]
        # y = args[1];
        # tmp1 = y-x*x;
        # # tmp2 = 1-x;
        # return self.pythonFunction(args)
        E = args[0]
        theta = args[1]
        L0 = args[2]
        return self.pythonFunction(E, theta, L0)


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

        return True

    def _defineDataset(self, wspace):
        rooVarSet = set()

        for aVarName in self.ranges.keys():
            rooVarSet.add(ROOT.RooRealVar(str(aVarName), str(aVarName), min(
                self._data[aVarName]), max(self._data[aVarName])))
        print(rooVarSet)
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

        rooVarSet = set()

        for aVarName in self.ranges.keys():
            if str(aVarName) == "x":
                rooVarSet.add(ROOT.RooRealVar(str(aVarName), str(aVarName), self.ranges[aVarName][0], self.ranges[aVarName][1]))
            else:
                rooVarSet.add(ROOT.RooRealVar(str(aVarName), str(aVarName), 1, self.ranges[aVarName][0], self.ranges[aVarName][1]))

        print(rooVarSet)
        # pdf = ROOT.RooGaussian("pdf", "pdf", x, mean, width)
        # try:
        self.func = getattr(self.module, self.function_name)
        print(self.func)
        # self.f = PyFunctionObject(self.func,len(self.ranges))
        self.f = PyFunctionObject(self.func, 3)
        # print(self.pyFuncObj)
        # self.f = ROOT.TPyMultiGenFunction(self.func)
        print(self.f)
        self.bindFunc = ROOT.RooFit.bindFunction("test", self.f, ROOT.RooArgList(*rooVarSet))
        # print(self.f.DoEval([1,1,1]))


        # // Construct parameter mean2 and sigma
        # mean = ROOT.RooRealVar("mean","mean",10,0,200) ;
        # sigma = ROOT.RooRealVar("sigma","sigma",3,0.1,10) ;

        # # // Construct interpreted function mean = sqrt(mean^2)
        # def testfunc(x, mean, sigma):
        #     return mean*sin(x*sigma) #1/sqrt(2*3.14159)*exp(-0.5*(x-mean)*(x-mean))
        # g2 = ROOT.RooFormulaVar("mean","mean","testfunc(x,mean,sigma)",ROOT.RooArgList(x,mean,sigma)) ;
        # gen = ROOT.RooGenericPdf("gen","@0",ROOT.RooArgList(g2))

        # // Construct a gaussian g2(x,sqrt(mean2),sigma) ;
        # g2 = ROOT.RooGaussian("g2","h2",x,mean,sigma) ;


        # // G e n e r a t e   t o y   d a t a
        # // ---------------------------------

        # // Construct a separate gaussian g1(x,10,3) to generate a toy Gaussian dataset with mean 10 and width 3
        # g1 = ROOT.RooGaussian("g1","g1",x,ROOT.RooFit.RooConst(10),ROOT.RooFit.RooConst(3)) ;
        # data2 = gen.generate(ROOT.RooArgSet(x),1000) ;
        # data2.Print()
        # xframe2 = x.frame(ROOT.RooFit.Title("Tailored Gaussian pdf")) ;
        # data2.plotOn(xframe2)
        # can = ROOT.TCanvas("can", "can", 600, 400)
        # xframe2.Draw() 
        # can.SaveAs("test.pdf")

        # except:
        #     logger.critical("I failed")
        x = ROOT.RooRealVar("x", "x", 0, -5, 5)
        a0 = ROOT.RooRealVar("a0","a0",0); 
        a0.setConstant(); 
        # RooChebychev will make a first order polynomial, set to a constant 
        bkg = ROOT.RooChebychev("a0_bkg","a0_bkg",x, ROOT.RooArgList(a0))
        # RooAbsReal *LSfcn = bindFunction(SH,m, RooArgList(deltaM,cw));//deltaM and cw are parameters 
        self.pdf = ROOT.RooRealSumPdf("pdf","pdf",self.bindFunc,bkg,ROOT.RooFit.RooConst(1.)) #; //combine the constant term (bkg)

        print("pdf:", self.pdf)
        getattr(wspace, 'import')(self.pdf)

        pdf = wspace.pdf("pdf")
        x = wspace.var("x")
        a = wspace.var("a")
        b = wspace.var("b")

        wspace.Print()
        x.Print()
        a.Print()
        # mean = ROOT.RooRealVar("mean", "mean", 0, -1, 1)
        # width = ROOT.RooRealVar("width", "width", 1., 0, 2)

        print(ROOT.RooArgSet(*rooVarSet))
        # pdf = ROOT.RooGaussian("pdf", "pdf", x, mean, width)
        data2 = pdf.generate(ROOT.RooArgSet(*rooVarSet),10000)
        data2.Print()
        xframe2 = x.frame(ROOT.RooFit.Title("Tailored Gaussian pdf")) ;
        data2.plotOn(xframe2)
        can = ROOT.TCanvas("can", "can", 600, 400)
        xframe2.Draw() 
        can.SaveAs("test.pdf")
        # self.pdf.generate(100)
        # try:
        #     self.results = getattr(self.module, self.function_name)(self.config_dict)
        #     return True
        # except Exception as err:
        #     logger.critical(err)
        #     return False

        # Save pdf: this will save all required variables and functions
        # getattr(wspace, 'import')(self.pdf)
        # print(wspace)
        # TF1 SH = new TF1("SH",signal_shape,x1,x2,nPar); // Define TF1 SH->SetParameters(a,b,c...); // set parameters - my function has 2
        # 3.) Bind the TF1 to a RooFit RooAbsReal, create a constant term, then use RooRealSumPdf (root.cern.ch/root/html/RooRealSumPdf.html 17) to create a PDF out of the function and the constant:
        # RooRealVar a0("a0","a0",0); 
        # a0.setConstant(kTRUE); 
        # //RooChebychev will make a first order polynomial, set to a constant 
        # RooChebychev bkg("bkg","bkg",m, RooArgList(a0)); //this is now a constant 
        # RooAbsReal *LSfcn = bindFunction(SH,m, RooArgList(deltaM,cw));//deltaM and cw are parameters 
        # RooAbsPdf *LSPdf = new RooRealSumPdf("LSPdf","LSPdf",*LSfcn,bkg,c1); //combine the constant term (bkg) and the term RooAbsReal (which is a function) into a PDF.
        # exit()
        return wspace


if __name__ == "__main__":
    rose = RosenBrock()
    f = ROOT.TPyMultiGenFunction(rose)
    x = ROOT.RooRealVar("x", "x", 0, 10)
    a = ROOT.RooRealVar("a", "a", 1, 2)
    fx = ROOT.RooFit.bindFunction("test", f, ROOT.RooArgList(x, a))
