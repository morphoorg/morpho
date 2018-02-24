import PhylloxeraPy
PhylloxeraPy.loadLibraries(True)


from morpho.utilities import morphologging, reader
from morpho.processors import BaseProcessor
logger = morphologging.getLogger(__name__)

import Constants

import ROOT

class RooFitLikelihoodSampler(BaseProcessor):

    def _defineDataset(self,wspace):
        '''
        Define our dataset given our data and add it to the workspace..
        Note that we only import one variable in the RooWorkspace.
        TODO:
         - Implement the import of several variables in the RooWorkspace
        '''
        var = ROOT.RooRealVar(self.varName,self.varName,min(self._data[self.varName]),max(self._data[self.varName]))
        data = ROOT.RooDataSet(self.datasetName,self.datasetName,ROOT.RooArgSet(var))
        for value in self._data[self.varName]:
            var.setVal(value)
            data.add(ROOT.RooArgSet(var))
        getattr(wspace,'import')(data)
        return wspace

    def definePdf(self,wspace):
        '''
        Defines the Pdf that RooFit will sample and add it to the workspace.
        Users should edit this method.
        '''
        logger.error("User should define this method in a child class!")
        raise
        # logger.debug("Defining pdf")

        # var = wspace.var(self.varName)

        # # Variables required by this model
        # m_nu = ROOT.RooRealVar("m_nu","m_nu",0.,0.,200) 
        # endpoint = ROOT.RooRealVar("endpoint", "endpoint", Constants.tritium_endpoint(),
        #                                                    Constants.tritium_endpoint()-100.,
        #                                                    Constants.tritium_endpoint()+100.)
        # meanSmearing = ROOT.RooRealVar("meanSmearing","meanSmearing",0.)
        # widthSmearing = ROOT.RooRealVar("widthSmearing","widthSmearing",0.00001,100)
        # NEvents = ROOT.RooRealVar("NEvents","NEvents",1.3212e+04,1e4,2e4)
        # NBkgd = ROOT.RooRealVar("NBkgd","NBkgd",5.3409e+03,1e3,1e4)
        # b = ROOT.RooRealVar("background","background",0.000001,-1,1)

        # # Spectrum pdf
        # spectrum = ROOT.RealTritiumSpectrum("spectrum","spectrum",var,endpoint,m_nu)

        # # Define PdfFactory to add background and smearing
        # pdffactory = ROOT.PdfFactory("myPdfFactory")

        # # Spectrum smearing
        # gauss = ROOT.RooGaussian("gauss","gauss",var,meanSmearing,widthSmearing)
        # smearedspectrum = pdffactory.GetSmearedPdf(ROOT.RealTritiumSpectrum)("smearedspectrum", 2, var, spectrum, meanSmearing, widthSmearing,100000)
        
        # # Background addition
        # background = ROOT.RooUniform("background","background",ROOT.RooArgSet(var))

        # # PDF of the model:
        # # this should have "pdf" as name 
        # pdf = pdffactory.AddBackground(ROOT.RooAbsPdf)("pdf",var,smearedspectrum,NEvents,NBkgd)
        
        # # can = ROOT.TCanvas("can","can",600,400)
        # # frame = var.frame()
        # # totalSpectrum.plotOn(frame)
        # # frame.Draw()
        # # can.SaveAs("plots/model.pdf") 

        # # Save pdf: this will save all required variables and functions
        # getattr(wspace,'import')(pdf)
        # return wspace

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self,value):
        self._data = value

    def _getArgSet(self,wspace,listNames):
        argSet = ROOT.RooArgSet()
        for name in listNames:
            argSet.add(wspace.var(name))
        return argSet

    def Configure(self, config_dict = {}):
        logger.info("Configure with {}".format(config_dict))
        self.varName = reader.read_param(config_dict,"varName", "required")
        self.datasetName = "data_"+self.varName
        self.nuisanceParametersNames = reader.read_param(config_dict,"nuisanceParams","required")
        self.paramOfInterestNames = reader.read_param(config_dict,"interestParams","required")
        self.iter = int(reader.read_param(config_dict,"iter",2000))
        self.warmup = int(reader.read_param(config_dict,"warmup",200))
        self.numCPU = int(reader.read_param(config_dict,"n_jobs",1))
        self.options = reader.read_param(config_dict,"options",{})

    def Run(self):
        logger.info("Run...")
        wspace = ROOT.RooWorkspace()
        wspace = self._defineDataset(wspace)
        wspace = self.definePdf(wspace)
        logger.debug("Workspace content:")
        wspace.Print()

        paramOfInterest = self._getArgSet(wspace,self.paramOfInterestNames)
        nuisanceParams = self._getArgSet(wspace,self.nuisanceParametersNames)
        allParams = ROOT.RooArgSet(paramOfInterest,nuisanceParams)

        dataset = wspace.data(self.datasetName)
        pdf = wspace.pdf("pdf")
        var = wspace.var(self.varName)
        width = wspace.var("widthSmearing")
        logger.debug("Creating likelihood")
        nll = pdf.createNLL(dataset,ROOT.RooFit.NumCPU(self.numCPU))
        
        logger.debug("Estimating best fits for proposal function...")
        result = pdf.fitTo(dataset,ROOT.RooFit.Save(),ROOT.RooFit.NumCPU(self.numCPU))
        logger.debug("...done!\nResults:")
        result.Print()
        
        can = ROOT.TCanvas("can","can",600,400)
        frame = var.frame()
        dataset.plotOn(frame)
        pdf.plotOn(frame)
        frame.Draw()
        can.SaveAs("plots/results_fit.pdf") 

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

        outputChain = {}
        for name in self.paramOfInterestNames:
            outputChain.update({name: []})
        outputChain.update({"lp_prob":[]})

        for i in range(0,chainData.numEntries()):
            # numberSamples = numberSamples + chainData.get(i).getRealValue("weight_MarkovChain_local_")
            for item in outputChain:
                if item == "lp_prob":
                    outputChain[item].append(-chainData.get(i).getRealValue("nll_MarkovChain_local_"))
                else:
                    outputChain[item].append(chainData.get(i).getRealValue(item))

        outputChain.update({"is_sample": [0]*self.warmup + [1]*(int(chainData.numEntries())-self.warmup)})
        
        return outputChain