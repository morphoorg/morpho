'''
Plot an histogram of the variables of interest
'''

from __future__ import absolute_import

from morpho.utilities import morphologging, reader
from morpho.processors import BaseProcessor
from morpho.processors.plots import RootCanvas, RootHistogram
logger=morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)

class Histogram(BaseProcessor):
    '''
    Describe.
    '''

    # @property
    # def data(self):
    #     return self._data

    # @data.setter
    # def data(self,value):
    #     self._data = value

    def _Configure(self, params):
        '''
        Configure
        '''
        # Initialize Canvas
        self.rootcanvas = RootCanvas.RootCanvas(params,optStat=0)
        self.histo = RootHistogram.RootHistogram(params,optStat=0)

        # Read other parameters
        self.namedata = reader.read_param(params,'data',"required")

    def _Run(self):
        self.histo.Fill(self.data.get(self.namedata))
        self.histo.Draw("hist")
        self.rootcanvas.Save()