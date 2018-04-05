'''
Plot an histogram of the variables of interest
'''

from __future__ import absolute_import

from morpho.utilities import morphologging, reader
from morpho.processors import BaseProcessor
from . import RootCanvas, RootHistogram
logger=morphologging.getLogger(__name__)

__all__ = []
__all__.append(__name__)

class Histogram(BaseProcessor):
    '''
    Processor that generates a canvas and a histogram and saves it.
    TODO:
    - Add the possibility to plot several histograms with the same binning on the same canvas
    - Generalize this processor so it understands if if should be a 1D or a 2D histogram
    '''

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
        self.rootcanvas.cd()
        self.histo.Draw("hist")
        self.rootcanvas.Save()