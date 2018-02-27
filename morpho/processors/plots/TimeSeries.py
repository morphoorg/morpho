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

        # Plot all histograms
        import ROOT    
        # Histograms must still be in memory when the pdf is saved
        for iName, name in enumerate(self.namedata):
            self.rootcanvas.cd(iName)
            g = ROOT.TGraph("name","name")
            subdata = self.data[name]
            for iValue, value in enumerate(subdata):
                g.SetPoint(iValue,iValue,value)
            g.Draw()
        self.rootcanvas.Save()