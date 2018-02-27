'''                                                                                                                                     
Plot a posteriori distribution of the variables of interest
'''

from __future__ import absolute_import

import json
import os


from morpho.utilities import morphologging, reader, plots
from morpho.processors import BaseProcessor
from morpho.processors.plots import RootCanvas
logger=morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)

class TimeSeries(BaseProcessor):
    '''                                                                                                                                
    Describe.
    '''

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self,value):
        self._data = value

    def Configure(self, param_dict):
        '''
        Configure
        '''
        logger.info("Configure with {}".format(param_dict))
        # Initialize Canvas
        self.rootcanvas = RootCanvas.RootCanvas(param_dict,optStat=0)

        # Read other parameters
        self.namedata = reader.read_param(param_dict,'data',"required")

    def Run(self):
        logger.info("Run...")
        # Drawing and dividing the canvas
        self.rootcanvas.Draw()
        self.rootcanvas.Divide(1,len(self.namedata))

        listGraph = []
        listGraphWarmup = []
        iWarmup = 0
        iSample = 0
        # Plot all histograms
        import ROOT    
        # Histograms must still be in memory when the pdf is saved
        for iName, name in enumerate(self.namedata):
            self.rootcanvas.cd(iName+1)
            listGraph.append(ROOT.TGraph())
            listGraphWarmup.append(ROOT.TGraph())
            subdata = self.data[str(name)]
            is_sample = self.data["is_sample"]
            iWarmup = 0
            iSample = 0
            for iValue, value in enumerate(subdata):
                if is_sample[iValue]:
                    listGraph[iName].SetPoint(iSample,iValue,value)
                    iSample = iSample+ 1
                else:
                    listGraphWarmup[iName].SetPoint(iWarmup,iValue,value)
                    iWarmup+=1
            print(iWarmup,iSample)
            listGraph[iName].Draw("AP")
            listGraph[iName].SetMarkerStyle(7)
            listGraphWarmup[iName].Draw("sameP")
            listGraphWarmup[iName].SetMarkerStyle(7)
            listGraphWarmup[iName].SetMarkerColor(2)
            listGraph[iName].SetTitle(";Iteration;{}".format(name))
            
        self.rootcanvas.Save()