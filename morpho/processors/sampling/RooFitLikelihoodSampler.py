'''
Base processor for RooFit-based samplers
Authors: M. Guigue
Date: 06/26/18
'''

import ROOT

from morpho.utilities import morphologging, reader
from morpho.processors import BaseProcessor
logger = morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)


class RooFitLikelihoodSampler(BaseProcessor):
    '''
    Base class for RooFit-based Likelihood sampling.
    A new class should inheritate from this one and have its
    own version of "definePdf".
    The input data are given via the attribute "data".
    '''

    def _defineDataset(self, wspace):
        '''
        Define our dataset given our data and add it to the workspace..
        Note that we only import one variable in the RooWorkspace.
        TODO:
         - Implement the import of several variables in the RooWorkspace
           -> might need to redefine this method when necessary
        '''
        var = ROOT.RooRealVar(self.varName, self.varName, min(self._data[self.varName]), max(self._data[self.varName]))
        if self.binned:
            data = ROOT.RooDataHist(self.datasetName, self.datasetName, ROOT.RooArgSet(var))
        else:
            data = ROOT.RooDataSet(self.datasetName, self.datasetName, ROOT.RooArgSet(var))
        for value in self._data[self.varName]:
            var.setVal(value)
            data.add(ROOT.RooArgSet(var))
        getattr(wspace, 'import')(data)
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
            argSet.add(wspace.var(name))
        return argSet

    def InternalConfigure(self, config_dict):
        self.varName = reader.read_param(config_dict, "varName", "required")
        self.datasetName = "data_"+self.varName
        self.nuisanceParametersNames = reader.read_param(config_dict, "nuisanceParams", "required")
        self.paramOfInterestNames = reader.read_param(config_dict, "interestParams", "required")
        self.iter = int(reader.read_param(config_dict, "iter", 2000))
        self.warmup = int(reader.read_param(config_dict, "warmup", 200))
        self.numCPU = int(reader.read_param(config_dict, "n_jobs", 1))
        self.binned = int(reader.read_param(config_dict, "binned", False))
        self.options = reader.read_param(config_dict, "options", dict())
        return True

    def InternalRun(self):
        wspace = ROOT.RooWorkspace()
        wspace = self._defineDataset(wspace)
        wspace = self.definePdf(wspace)
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
        result = pdf.fitTo(dataset, ROOT.RooFit.Save(), ROOT.RooFit.NumCPU(self.numCPU))
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
                    self.results[item].append(-chainData.get(i).getRealValue("nll_MarkovChain_local_"))
                else:
                    self.results[item].append(chainData.get(i).getRealValue(item))

        self.results.update({"is_sample": [0]*self.warmup + [1]*(int(chainData.numEntries())-self.warmup)})

        return True
