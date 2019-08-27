'''
Base processor for RooFit-based samplers
Authors: M. Guigue
Date: 06/26/18
'''

try:
    import ROOT
except ImportError:
    pass

import random

from morpho.utilities import morphologging, reader
from morpho.processors import BaseProcessor
logger = morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)


class RooFitInterfaceProcessor(BaseProcessor):
    '''
    Base class for RooFit-based sampling.
    A new class should inheritate from this one and have its
    own version of "definePdf".
    The input data are given via the attribute "data".

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

    Input:
        data: dictionary containing model input data

    Results:
        results: dictionary containing the result of the sampling of the parameters of interest
    '''

    def _defineDataset(self, wspace):
        '''
        Define our dataset given our data and add it to the workspace..
        Note that we only import one variable in the RooWorkspace.
        TODO:
         - Implement the import of several variables in the RooWorkspace
           -> might need to redefine this method when necessary
        '''
        var = ROOT.RooRealVar(self.varName, self.varName, min(
            self._data[self.varName]), max(self._data[self.varName]))
        # Needed for being able to do convolution products on this variable (don't touch!)
        var.setBins(10000, "cache")
        if self.binned:
            logger.debug("Binned dataset {}".format(self.varName))
            data = ROOT.RooDataHist(
                self.datasetName, self.datasetName, ROOT.RooArgSet(var))
        else:
            logger.debug("Unbinned dataset {}".format(self.varName))
            data = ROOT.RooDataSet(
                self.datasetName, self.datasetName, ROOT.RooArgSet(var))
        for value in self._data[self.varName]:
            var.setVal(value)
            data.add(ROOT.RooArgSet(var))        
        getattr(wspace, 'import')(data)
        logger.info("Workspace after dataset:")
        wspace.Print()
        return wspace

    def definePdf(self, wspace):
        '''
        Defines the Pdf that RooFit will sample and add it to the workspace.
        The Workspace is then returned by the user.
        Users should always create their own method.
        '''
        logger.error("User should define this method in a child class!")
        raise

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    def _getArgSet(self, wspace, listNames):
        argSet = ROOT.RooArgSet()
        for name in listNames:
            logger.debug("{} -> {}".format(name, wspace.var(name)))
            argSet.add(wspace.var(name))
        return argSet

    def InternalConfigure(self, config_dict):
        self.varName = reader.read_param(config_dict, "varName", "required")
        self.mode = reader.read_param(config_dict, "mode", "generate")
        logger.debug("Mode {}".format(self.mode))
        if self.mode == "lsampling" or self.mode == "generate":
            self.iter = int(reader.read_param(config_dict, "iter", "required"))
        if self.mode == "fit" or self.mode == "lsampling":
            self.binned = int(reader.read_param(config_dict, "binned", False))
        if self.mode == "lsampling":
            self.nuisanceParametersNames = reader.read_param(
                config_dict, "nuisanceParams", "required")
            self.warmup = int(reader.read_param(
                config_dict, "warmup", self.iter/2.))
        self.numCPU = int(reader.read_param(config_dict, "n_jobs", 1))
        self.options = reader.read_param(config_dict, "options", dict())
        if self.mode not in ['generate', 'lsampling', 'fit']:
            logger.error(
                "Mode '{}' is not valid; choose between 'mode' and 'lsampling'".format(self.mode))
            return False
        self.datasetName = "data_"+self.varName
        self.paramOfInterestNames = reader.read_param(
            config_dict, "interestParams", "required")
        self.fixedParameters = reader.read_param(
            config_dict, "fixedParams", dict)
        self.make_fit_plot = reader.read_param(
            config_dict, "make_fit_plot", False)
        if not isinstance(self.fixedParameters, dict):
            logger.error(
                "fixedParams should be a dictionary like {'varName': value}")
            return False
        return True

    def InternalRun(self):
        if self.mode == "generate":
            return self._Generator()
        elif self.mode == 'lsampling':
            return self._LikelihoodSampling()
        elif self.mode == 'fit':
            return self._Fit()
        else:
            logger.error("Unknown mode <{}>".format(self.mode))
            return False

    def _Fit(self):
        '''
        Fit the data using the pdf defined in the workspace
        '''
        wspace = ROOT.RooWorkspace()
        wspace = self._defineDataset(wspace)
        wspace = self.definePdf(wspace)
        logger.debug("Workspace content:")
        wspace.Print()
        wspace = self._FixParams(wspace)
        pdf = wspace.pdf("pdf")
        dataset = wspace.data(self.datasetName)
        dataset.Print()

        paramOfInterest = self._getArgSet(wspace, self.paramOfInterestNames)
        result = pdf.fitTo(dataset, ROOT.RooFit.Save())
        result.Print()

        if self.make_fit_plot:
            can = ROOT.TCanvas("can", "can", 600, 400)
            var = wspace.var(self.varName)
            frame = var.frame()
            dataset.plotOn(frame)
            pdf.plotOn(frame)
            frame.Draw()
            can.SaveAs("results_fit.pdf")

        self.result = {}
        for varName in self.paramOfInterestNames:
            self.result.update(
                {str(varName): wspace.var(str(varName)).getVal()})
            self.result.update(
                {"error_"+str(varName): wspace.var(str(varName)).getErrorHi()})
        return True

    def _FixParams(self, wspace):
        '''Fix the variables inside a workspace'''
        if len(self.fixedParameters) == 0:
            logger.debug("No fixed parameters given")
            return wspace
        for varName, value in self.fixedParameters.items():
            wspace.var(str(varName)).setVal(float(value))
            wspace.var(str(varName)).setConstant()
            logger.debug("Value of {} set to {}".format(
                varName, wspace.var(str(varName)).getVal()))
        return wspace

    def _Generator(self):
        '''
        Generate the data by sampling the pdf defined in the workspace
        '''
        # Setting a random seed
        ROOT.RooRandom.randomGenerator().SetSeed(random.randint(0, 121212111121212))

        wspace = ROOT.RooWorkspace()
        wspace = self.definePdf(wspace)
        logger.debug("Workspace content:")
        wspace.Print()
        wspace = self._FixParams(wspace)
        pdf = wspace.pdf("pdf")
        paramOfInterest = self._getArgSet(wspace, self.paramOfInterestNames)
        paramOfInterest.Print()
        data = pdf.generate(paramOfInterest, self.iter)
        data.Print()

        self.data = {}
        for name in self.paramOfInterestNames:
            self.data.update({name: []})

        for i in range(0, data.numEntries()):
            for item in self.data:
                self.data[item].append(
                    data.get(i).getRealValue(item))
        self.data.update({"is_sample": [1]*(self.iter)})

        return True

    def _LikelihoodSampling(self):
        '''
        Sample the pdf defined in the workspace
        '''
        wspace = ROOT.RooWorkspace()
        wspace = self._defineDataset(wspace)
        wspace = self.definePdf(wspace)
        wspace = self._FixParams(wspace)
        logger.debug("Workspace content:")
        wspace.Print()
        paramOfInterest = self._getArgSet(wspace, self.paramOfInterestNames)
        nuisanceParams = self._getArgSet(wspace, self.nuisanceParametersNames)
        allParams = ROOT.RooArgSet(paramOfInterest, nuisanceParams)

        dataset = wspace.data(self.datasetName)
        pdf = wspace.pdf("pdf")

        logger.debug("Creating likelihood")
        nll = pdf.createNLL(dataset, ROOT.RooFit.NumCPU(self.numCPU))

        logger.debug("Estimating best fits for proposal function...")
        result = pdf.fitTo(dataset, ROOT.RooFit.Save(),
                           ROOT.RooFit.NumCPU(self.numCPU))
        logger.debug("...done!\nResults:")
        result.Print()
        logger.debug("Covariance matrix:")
        result.covarianceMatrix().Print()

        # can = ROOT.TCanvas("can","can",600,400)
        # var = wspace.var(self.varName)
        # frame = var.frame()
        # dataset.plotOn(frame)
        # pdf.plotOn(frame)
        # frame.Draw()
        # can.SaveAs("plots/results_fit.pdf")

        logger.debug("Define Proposal function")
        ph = ROOT.RooStats.ProposalHelper()
        ph.SetVariables(result.floatParsFinal())
        ph.SetCovMatrix(result.covarianceMatrix())
        ph.SetUpdateProposalParameters(True)
        ph.SetCacheSize(1000)
        pdfProp = ph.GetProposalFunction()

        mh = ROOT.RooStats.MetropolisHastings()
        mh.SetFunction(nll)
        mh.SetType(ROOT.RooStats.MetropolisHastings.kLog)
        mh.SetSign(ROOT.RooStats.MetropolisHastings.kNegative)
        mh.SetParameters(allParams)
        mh.SetProposalFunction(pdfProp)
        mh.SetNumIters(self.iter)
        mh.SetNumBurnInSteps(self.warmup)
        logger.debug("Starting Markov Chain...")
        chain = mh.ConstructChain()
        logger.debug("Markov Chain complete!")

        chainData = chain.GetAsDataSet()

        self.results = {}
        for name in self.paramOfInterestNames:
            self.results.update({name: []})
        self.results.update({"lp_prob": []})

        for i in range(0, chainData.numEntries()):
            for item in self.results:
                if item == "lp_prob":
                    self.results[item].append(-chainData.get(
                        i).getRealValue("nll_MarkovChain_local_"))
                else:
                    self.results[item].append(
                        chainData.get(i).getRealValue(item))
        self.results.update(
            {"is_sample": [0]*self.warmup + [1]*(int(chainData.numEntries())-self.warmup)})

        return True
